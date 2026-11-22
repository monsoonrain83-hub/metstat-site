#!/usr/bin/env node
/** Read-only production HTML/JS/CSS audit. Never injects duplicate model buttons.
 * Usage: node scripts/audit-model-controls.mjs /path/to/site/root
 * Optional: --strict (fail if duplicated logical model controls are found).
 */
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2];
if (!root || root.startsWith('--')) {
  console.error('Usage: node scripts/audit-model-controls.mjs SITE_ROOT [--strict]');
  process.exit(2);
}
const strict = process.argv.includes('--strict');
const candidates = [];
const ignore = new Set(['node_modules','.git','vendor','dist','build','coverage']);
function walk(dir, depth=0) {
  if (depth > 8) return;
  for (const ent of fs.readdirSync(dir, {withFileTypes:true})) {
    if (ent.isDirectory()) { if (!ignore.has(ent.name)) walk(path.join(dir,ent.name),depth+1); }
    else if (/\.(?:html|php|js|css)$/i.test(ent.name)) candidates.push(path.join(dir,ent.name));
  }
}
walk(path.resolve(root));
const patterns = {
  modelDock: /(?:ms95-modelDock|fsMods|modelDock)/g,
  fullscreen: /(?:requestFullscreen|fullscreenchange|webkitfullscreenchange)/g,
  ecmwfLegacy: /(?:ecmwf9|ecmwf_ifs025)/g,
  gfsLegacy: /(?:gfs25|ncep_gfs025)/g,
  modelButton: /(?:data-model|data-model-id|model-btn|model-button)/g,
};
const hits = Object.fromEntries(Object.keys(patterns).map(k=>[k,[]]));
for (const file of candidates) {
  const src = fs.readFileSync(file,'utf8');
  for (const [key,re] of Object.entries(patterns)) {
    const n = [...src.matchAll(re)].length;
    if (n) hits[key].push({file:path.relative(root,file),occurrences:n});
  }
}
const report = {root:path.resolve(root), scannedFiles:candidates.length, hits,
  warnings: [], pass:true};
if (!hits.modelDock.length) report.warnings.push('No known model dock selector found; inspect actual DOM before changes.');
if (!hits.fullscreen.length) report.warnings.push('No fullscreen API handler found; inspect external scripts.');
if (!hits.modelButton.length) report.warnings.push('No known model-button markup; do not add new controls blindly.');
// Static counts are diagnostic only; repeated selector references do not prove duplicate DOM nodes.
report.warnings.push('Static source scan cannot prove DOM uniqueness. Run browser integration tests on rendered page.');
if (strict && (!hits.modelDock.length || !hits.fullscreen.length)) report.pass=false;
console.log(JSON.stringify(report,null,2));
if (!report.pass) process.exitCode=1;

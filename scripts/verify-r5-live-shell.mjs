#!/usr/bin/env node
/** Read-only release gate for MetStat's ONE desktop layout (all devices). */
import fs from 'node:fs';
const filename=process.argv[2];
if (!filename) { console.error('Usage: node verify-r5-live-shell.mjs index.html');process.exit(2); }
let s;
try{s=fs.readFileSync(filename,'utf8')}catch(e){console.error(String(e));process.exit(2)}
const assertions={
  correct_document: /<html[^>]+lang=["']fa["'][^>]*dir=["']rtl["']/.test(s),
  device_viewport: /<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1/.test(s),
  no_phone_fit_script: !s.includes('id="ms9-phone-fit"'),
  desktop_horizontal_overflow: /min-width:960px!important/.test(s)&&/overflow-x:auto!important/.test(s),
  seven_menu_shell: s.includes('ms7Nav')&&s.includes('ms7-group'),
  red_r5_token: s.includes('#DC1937'),
  sky_r5_token: s.includes('#399FD4'),
  native_map_controls: s.includes('id="nvStage"')&&s.includes('id="nvCv"'),
  real_map_geometry: s.includes('html.ms9-active #onViewer>.nvCard>.nvStage'),
  no_broken_contents_experiment: !s.includes('/* Experiment: one r5 workspace where original native controls are direct CSS-grid items.'),
  guest_site_access: s.includes('const AUTH_ALL=false')&&s.includes('const AUTH_MODES=[]'),
};
const failed=Object.entries(assertions).filter(([_,ok])=>!ok).map(([name])=>name);
const report={input:filename,checks:assertions,passed:failed.length===0,failed};
console.log(JSON.stringify(report,null,2));
process.exit(failed.length?1:0);

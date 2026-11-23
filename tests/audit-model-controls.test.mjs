import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const script=path.resolve('scripts/audit-model-controls.mjs');
test('audit discovers existing fullscreen and model controls without modifying site',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'metstat-audit-'));
  try {
    const file=path.join(dir,'index.html');
    const html='<button data-model="ecmwf">ECMWF</button><div id="fsMods"></div><script>document.body.requestFullscreen()</script>';
    fs.writeFileSync(file,html);
    const result=spawnSync(process.execPath,[script,dir,'--strict'],{encoding:'utf8'});
    assert.equal(result.status,0,result.stderr);
    assert.equal(JSON.parse(result.stdout).scannedFiles,1);
    assert.equal(fs.readFileSync(file,'utf8'),html);
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
});
test('strict audit fails closed when no fullscreen controls are present',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'metstat-audit-'));
  try {
    fs.writeFileSync(path.join(dir,'index.html'),'<main>test</main>');
    const result=spawnSync(process.execPath,[script,dir,'--strict'],{encoding:'utf8'});
    assert.equal(result.status,1);
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
});

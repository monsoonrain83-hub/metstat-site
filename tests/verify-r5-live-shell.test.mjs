import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const gate = path.resolve('scripts/verify-r5-live-shell.mjs');
const fixture='<html lang="fa" dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=5"></head><body>ms7Nav ms7-group #DC1937 #399FD4 id="nvStage" id="nvCv" html.ms9-active #onViewer>.nvCard>.nvStage min-width:960px!important overflow-x:auto!important const AUTH_ALL=false const AUTH_MODES=[]</body></html>';
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ms-r5-'));
try{
 test('accepts one-desktop shell as preflight candidate',()=>{const f=path.join(tmp,'good.html');fs.writeFileSync(f,fixture);const p=spawnSync(process.execPath,[gate,f],{encoding:'utf8'});assert.equal(p.status,0,p.stdout+p.stderr);});
 test('rejects phone-fit and forced login',()=>{const f=path.join(tmp,'bad.html');fs.writeFileSync(f,fixture.replace('const AUTH_ALL=false','const AUTH_ALL=true')+'id="ms9-phone-fit"');const p=spawnSync(process.execPath,[gate,f],{encoding:'utf8'});assert.equal(p.status,1,p.stdout+p.stderr);assert.match(p.stdout,/guest_site_access/);});
 test('rejects missing input',()=>{const p=spawnSync(process.execPath,[gate],{encoding:'utf8'});assert.equal(p.status,2);});
}finally{process.on('exit',()=>fs.rmSync(tmp,{recursive:true,force:true}));}

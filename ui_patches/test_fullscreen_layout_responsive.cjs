/* r205: fail-closed fullscreen layout, only original chips, small observer scope. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const css=fs.readFileSync(__dirname+'/metstat_original_model_chips_horizontal.css','utf8');
const js=fs.readFileSync(__dirname+'/metstat_original_model_chips_horizontal.js','utf8');
assert.match(css,/#nvFs\[data-original-chips-horizontal="1"\] \.fsRow\.fsA #fsMods/);
assert.match(css,/overflow-x:auto!important/);
assert.match(css,/right:110px!important;left:80px!important/);
assert.match(css,/@media\(max-width:540px\)/);
assert.match(css,/right:100px!important;left:55px!important/);
assert.match(css,/#nvFs\[data-original-chips-horizontal="1"\] \.fsColR \.fsModDd\{display:none!important\}/);
assert.match(js,/fs\.querySelectorAll\('#fsMods'\)\.length !== 1/);
assert.match(js,/if \(!top \|\| !chips \|\| !oldMenu\) return false/);
assert.match(js,/watch\.observe\(document\.body, \{ childList: true \}\)/);
assert.doesNotMatch(js,/subtree: ?true|cloneNode/);
assert.ok(js.indexOf("fs.setAttribute(MARKER, '1')") < js.indexOf('oldMenu.hidden = true'));
console.log('r205 production guard static checks: PASS');

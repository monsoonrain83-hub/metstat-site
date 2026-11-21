/* MetStat fullscreen r204: no duplicate chips, portrait width remains usable. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const css=fs.readFileSync(__dirname+'/metstat_original_model_chips_horizontal.css','utf8');
assert.match(css,/#nvFs \.fsRow\.fsA #fsMods/);
assert.match(css,/overflow-x:auto!important/);
assert.match(css,/right:110px!important;left:80px!important/);
assert.match(css,/@media\(max-width:540px\)/);
assert.match(css,/right:100px!important;left:55px!important/);
assert.match(css,/#nvFs \.fsColR \.fsModDd\{display:none!important\}/);
assert.doesNotMatch(css,/cloneNode|createElement/);
console.log('Fullscreen r204 CSS constraints PASS: original group only, portrait width, no overlapping dropdown');

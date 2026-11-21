const assert=require('node:assert/strict');
const m=require('./metstat_scoped_station_search.js');
const rows=[
{name_fa:'بوژان',province:'خراسان رضوی',county:'نیشابور',lat:36.2,lon:58.9,type:'rain'},
{name_fa:'نیشابور',province:'خراسان رضوی',county:'نیشابور',lat:36.1,lon:58.8},
{name_fa:'قاسم آباد',province:'فارس',county:'داراب',lat:28.7,lon:54.4},
{name_fa:'قاسم آباد',province:'خراسان رضوی',county:'مشهد',lat:36.3,lon:59.5},
{name_fa:'بوژان',province:'خراسان رضوی',county:'نیشابور',lat:'',lon:''}
];
assert.equal(m.parse('نیشابور : بوژان').station,'بوژان');
assert.equal(m.resolve(rows,'نیشابور: بوژان',{provinces:['خراسان رضوی']}).status,'review');
assert.equal(m.resolve(rows.slice(0,4),'نیشابور: بوژان',{provinces:['خراسان رضوی']}).match.name_fa,'بوژان');
assert.equal(m.resolve(rows,'قاسم آباد',{provinces:['خراسان رضوی']}).match.county,'مشهد');
assert.equal(m.resolve(rows,'قاسم آباد',{provinces:['گلستان']}).status,'unresolved');
assert.equal(m.resolve(rows,'نیشابور: بوژان',{provinces:['فارس']}).status,'unresolved');
assert.equal(m.resolve(rows,'قاسم آباد').status,'review');
console.log('7 scoped station matching checks passed');

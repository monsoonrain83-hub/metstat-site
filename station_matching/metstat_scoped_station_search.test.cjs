const assert=require('node:assert/strict');
const m=require('./metstat_scoped_station_search.js');
const rows=[
{name_fa:'بوژان',province:'خراسان رضوی',county:'نیشابور',lat:36.2,lon:58.9,type:'rain'},
{name_fa:'نیشابور',province:'خراسان رضوی',county:'نیشابور',lat:36.1,lon:58.8},
{name_fa:'قاسم آباد',province:'فارس',county:'داراب',lat:28.7,lon:54.4,type:'raingauge'},
{name_fa:'قاسم آباد',province:'خراسان رضوی',county:'مشهد',lat:36.3,lon:59.5,type:'raingauge'},
{name_fa:'بوژان',province:'خراسان رضوی',county:'نیشابور',lat:'',lon:''}
];
assert.equal(m.parse('نیشابور : بوژان').station,'بوژان');
assert.equal(m.resolve(rows,'نیشابور: بوژان',{provinces:['خراسان رضوی']}).status,'review');
// An exact second site with missing coordinates must block auto-confirmation.
assert.equal(m.resolve(rows,'بوژان',{provinces:['خراسان رضوی']}).status,'review');
assert.equal(m.resolve(rows.slice(0,4),'نیشابور: بوژان',{provinces:['خراسان رضوی']}).match.name_fa,'بوژان');
assert.equal(m.resolve(rows,'قاسم آباد',{provinces:['خراسان رضوی']}).match.county,'مشهد');
assert.equal(m.resolve(rows,'قاسم آباد',{provinces:['گلستان']}).status,'unresolved');
assert.equal(m.resolve(rows,'نیشابور: بوژان',{provinces:['فارس']}).status,'unresolved');
assert.equal(m.resolve(rows,'قاسم آباد').status,'review');
assert.equal(m.resolve(rows.slice(0,4),'بوژان',{provinces:['خراسان رضوی']}).status,'confirmed');
assert.equal(m.resolve(rows,'بوژان',{provinces:['گلستان']}).status,'unresolved');
const osmOnly=[{name_fa:'بوژان',type:'village',province:'خراسان رضوی',county:'نیشابور',lat:36.21,lon:58.9,status:'OSM_place_unverified_station'}];
assert.equal(m.resolve(osmOnly,'بوژان',{provinces:['خراسان رضوی']}).status,'review','An OSM locality must never be confirmed as a rain gauge');
assert.equal(m.resolve(osmOnly,'بوژان',{provinces:['خراسان رضوی']}).match,null);
const realGauge={name_fa:'بوژان',type:'raingauge',province:'خراسان رضوی',county:'نیشابور',lat:36.22,lon:58.91};
assert.equal(m.resolve([...osmOnly,realGauge],'بوژان',{provinces:['خراسان رضوی']}).match,realGauge,'A unique real sensor can outrank a same-name village');
assert.equal(m.resolve([...osmOnly,realGauge,{...realGauge,lat:36.3}],'بوژان',{provinces:['خراسان رضوی']}).status,'review','Two station candidates need human review');
assert.equal(m.resolve([{name_fa:'ایستگاه نامعلوم',province:'فارس',lat:28.3,lon:54.5}],'ایستگاه نامعلوم',{provinces:['فارس']}).status,'review','Unknown type is not an attested sensor');
assert.equal(m.resolve([{...realGauge,province:''}],'بوژان',{provinces:['خراسان رضوی']}).status,'unresolved','Missing province cannot pass hard geographic scope');
assert.equal(m.resolve([{...realGauge,type:'hydrometric'}],'بوژان',{provinces:['خراسان رضوی']}).status,'confirmed');
console.log('17 scoped station matching checks passed');

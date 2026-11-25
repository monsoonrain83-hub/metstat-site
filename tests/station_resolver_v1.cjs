const assert=require('node:assert/strict');const r=require('../station_resolver_v1.js');
const stations=[{id:'b',nameFa:'بوژان',lat:36.1,lon:59.2,province:'خراسان رضوی',county:'نیشابور',type:'raingauge'},{id:'n',nameFa:'نیشابور',lat:36.2,lon:59.6,province:'خراسان رضوی',county:'نیشابور',type:'synoptic'},{id:'q',nameFa:'قاسم آباد',lat:29.1,lon:53.2,province:'فارس',county:'استهبان',type:'raingauge'},{id:'m',nameFa:'قاسم آباد',lat:36.2,lon:59.5,province:'خراسان رضوی',county:'مشهد',type:'raingauge'}];
assert.equal(r.resolve('نیشابور: بوژان',stations).candidate.id,'b');
assert.equal(r.resolve('قاسم آباد',stations,{province:'خراسان رضوی'}).candidate.id,'m');
assert.equal(r.resolve('قاسم آباد',stations).status,'ambiguous');
assert.equal(r.resolve('نیشابور: بوژان',stations,{province:'فارس'}).status,'unresolved');
assert.equal(r.scopeFromText('ایستگاههای استان خراسان رضوی',['فارس','خراسان رضوی'],['مشهد']).province,'خراسان رضوی');
assert.equal(r.scopeFromText('ایستگاههای شهر مشهد',['فارس'],['مشهد']).city,'مشهد');
assert.equal(r.resolve('بوژان',[...stations,{...stations[0],id:'other',lat:37}]).status,'ambiguous');
const key=r.resolve('نیشابور: بوژان',stations).key;
assert.equal(r.resolve('نیشابور: بوژان',stations,{}, {[key]:'b'}).reason,'learned_verified_override');

for(const bad of ['', '   ', null, false, true, 0, NaN, Infinity, 'abc', 23, 42]){
 assert.equal(r.resolve('بوژان',[{...stations[0],lat:bad}]).status,'unresolved');
}
assert.equal(r.resolve('بوژان',[{...stations[0],lon:100}]).status,'unresolved');
assert.equal(r.resolve('بوژان',[{...stations[0],province:'  '}]).status,'unresolved');
assert.equal(r.resolve('بوژان',[null,{...stations[0],aliases:'بوژان'}]).status,'verified');
assert.equal(r.resolve('بوژان',[{...stations[0],lat:'36.1',lon:'59.2'}]).status,'verified');
assert.equal(r.resolve('بوژان',[stations[0],{...stations[0],province:'فارس',id:'other'}]).status,'ambiguous');
const inherited=Object.create({[key]:'b'});
assert.equal(r.resolve('نیشابور: بوژان',stations,{},inherited).reason,'unique_exact');

console.log('context-aware station resolver tests passed');

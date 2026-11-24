const assert=require('node:assert/strict');
const s=require('../station_name_suggestions.js');
const records=[
 {id:'e',nameFa:'استهبان',nameEn:'Estahban',province:'فارس',county:'استهبان',lat:29.1,lon:54},
 {id:'b',nameFa:'بوژان',nameEn:'Buzhan',province:'خراسان رضوی',county:'نیشابور',lat:36.1,lon:59.2},
 {id:'p',nameFa:'پیوه ژن',province:'خراسان رضوی',county:'مشهد',lat:36.2,lon:59.5},
 {id:'q1',nameFa:'قاسم آباد',province:'فارس',county:'استهبان',lat:29.1,lon:53.2},
 {id:'q2',nameFa:'قاسم آباد',province:'خراسان رضوی',county:'مشهد',lat:36.2,lon:59.5}
];
assert.equal(s.suggest('Estahban',records)[0].candidate.id,'e');
assert.equal(s.suggest('Estahbann',records)[0].candidate.id,'e');
assert.equal(s.suggest('استهبان',records)[0].score,100);
assert.equal(s.suggest('پيـوه‌ژن',records)[0].candidate.id,'p');
assert.equal(s.suggest('پیوهژن',records)[0].reason,'spacing_variant');
assert.equal(s.suggest('Piveh Zhan',records)[0].candidate.id,'p');
assert.equal(s.suggest('نیشابور: بوژان',records)[0].candidate.id,'b');
assert.equal(s.suggest('قاسم آباد',records).length,2);
assert.equal(s.suggest('قاسم‌آباد',records,{province:'فارس'})[0].candidate.id,'q1');
assert.equal(s.suggest('قاسم آباد',records,{province:'اردبیل'}).length,0);
assert.equal(s.suggest('نیشابور: بوژان',records,{county:'مشهد'}).length,0);
assert.equal(s.suggest('نیشابور',records).length,0);
assert.equal(s.suggest('بوژان',[{...records[1],lat:''}]).length,0);
assert.equal(s.suggest('بوژان',[{...records[1],province:''}]).length,0);
assert.equal(s.suggest('بوژان',[null,records[1]])[0].requiresConfirmation,true);
assert.equal(s.suggest('قاسم آباد',records).every(x=>x.requiresConfirmation),true);
assert.equal(s.suggest('',records).length,0);
assert.equal(s.suggest('قاسم آباد',records,{},1).length,1);
console.log('18 station suggestion regression assertions passed');

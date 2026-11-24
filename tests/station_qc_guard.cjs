const assert=require('node:assert/strict');const q=require('../station_qc_guard.js');
assert.deepEqual(q.parse('نیشابور: بوژان').district,'نیشابور');
assert.equal(q.parse('نیشابور: بوژان').station,'بوژان');
assert.equal(q.eligible('نیشابور: بوژان',{name:'نیشابور',lat:36,lon:59,province:'خراسان رضوی',district:'نیشابور'}).ok,false);
assert.equal(q.eligible('فرودگاه',{name:'فرودگاه اردبیل',lat:38,lon:48,province:'اردبیل'}).ok,false);
assert.equal(q.eligible('کارده',{name:'کورده',lat:36,lon:59,province:'خراسان رضوی'}).ok,false);
assert.equal(q.eligible('دانشگاه فردوسی',{name:'فردوس',lat:36,lon:59,province:'خراسان رضوی'}).ok,false);
assert.equal(q.eligible('بوژان',{name:'بوژان',province:'خراسان رضوی'}).reason,'unverified_coordinates');
assert.equal(q.eligible('نیشابور: بوژان',{name:'بوژان',lat:36,lon:59,province:'خراسان رضوی',district:'نیشابور'}).ok,true);
assert.equal(q.eligible('نیشابور: بوژان',{name:'بوژان',lat:36,lon:59,province:'خراسان رضوی',district:'سبزوار'}).ok,false);
assert.equal(q.norm('پيـوه‌ژن'),'پیوه ژن');
const c={name:'بوژان',aliases:['بوژان','بو ژان'],lat:36,lon:59,province:'خراسان رضوی',district:'نیشابور'};
assert.equal(q.choose('نیشابور: بو ژان',[c]).ok,true);
assert.equal(q.choose('نیشابور: بوژان',[c,{...c,lat:36.1}]).reason,'ambiguous_georeferenced_candidates');
assert.equal(q.choose('نیشابور: بوژان',[{...c,lat:null}]).ok,false);

for(const bad of ['', '   ', null, false, true, 0, NaN, Infinity, 'abc', 23, 42]){
 assert.equal(q.eligible('بوژان',{...c,lat:bad}).reason,'unverified_coordinates');
}
assert.equal(q.eligible('بوژان',{...c,province:'   '}).reason,'missing_province');
assert.equal(q.eligible('بوژان',{...c,lat:'36',lon:'59'}).ok,true);
assert.equal(q.choose('بوژان',[null,c]).ok,true);

console.log('station QC guard passed');

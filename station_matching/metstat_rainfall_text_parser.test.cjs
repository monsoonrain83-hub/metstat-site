const assert=require('node:assert/strict');
const p=require('./metstat_rainfall_text_parser.js');
const scope=require('./metstat_scoped_station_search.js');
const rows=[
 {id:'B',name_fa:'بوژان',county:'نیشابور',province:'خراسان رضوی',lat:36.2,lon:58.9},
 {id:'N',name_fa:'نیشابور',county:'نیشابور',province:'خراسان رضوی',lat:36.1,lon:58.8},
 {id:'M',name_fa:'مشهد',county:'مشهد',province:'خراسان رضوی',lat:36.3,lon:59.6},
 {id:'F',name_fa:'مشهد',county:'فسا',province:'فارس',lat:28.9,lon:53.6}
];
assert.equal(p.parse('نیشابور: بوژان ۴۲ میلی‌متر').rows[0].name,'نیشابور: بوژان');
assert.equal(p.parse('قوچان ۱۰۰ میلی متر').rows[0].amount,100);
assert.equal(p.parse('مشهد بیست و پنج میلی متر').rows[0].amount,25);
assert.equal(p.parse('مشهد ۲۵٫۵ mm').rows[0].amount,25.5);
assert.equal(p.parse('بوژان: ۲۵').rows[0].name,'بوژان');
assert.equal(p.parse('مشهد 25; نیشابور: بوژان 30').rows.length,2);
assert.equal(p.parse('سرفصل بدون عدد').errors.length,1);
const x=p.resolveText('نیشابور: بوژان ۴۲\nمشهد ۲۵',rows,scope,['خراسان رضوی']);
assert.equal(x.results[0].match.match.id,'B');
assert.equal(x.results[1].match.match.id,'M');
const y=p.resolveText('مشهد ۲۵',rows,scope,['گلستان']);
assert.equal(y.results[0].match.status,'unresolved');
assert.equal(p.parse('مشهد ۳۰۰۰۰ میلی‌متر').rows.length,0);
const h=p.resolveText('ایستگاه‌های استان خراسان رضوی\\nمشهد ۲۵\\nنیشابور: بوژان ۴۲',rows,scope,[]);
assert.equal(h.results.length,2);
assert.equal(h.results[0].match.match.id,'M');
assert.equal(h.results[1].match.match.id,'B');
assert.equal(h.errors.length,0);
const conflict=p.resolveText('ایستگاه‌های استان خراسان رضوی\\nمشهد ۲۵',rows,scope,['فارس']);
assert.equal(conflict.results[0].match.status,'unresolved');
assert.equal(conflict.results[0].match.reason,'header_outside_selected_provinces');
const inCity=p.resolveText('ایستگاه‌های شهر مشهد\\nمشهد ۲۵',rows,scope,[]);
assert.equal(inCity.results[0].match.match.id,'M');
console.log('17 Persian rainfall parsing and geographic scope checks passed');

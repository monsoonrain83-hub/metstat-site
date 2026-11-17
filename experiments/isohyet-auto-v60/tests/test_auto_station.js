const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const P=require('../online/assets/metstat_rain_parser.js');
const M=require('../online/assets/metstat_auto_match.js');
const report=fs.readFileSync(__dirname+'/gilan_report_1405-08-26.txt','utf8');
test('Gilan v59 regression: 46 intact rainfall rows with correct extremes',()=>{
 const a=P.parseRainReport(report);
 assert.equal(a.province,'گیلان');assert.equal(a.count,46);assert.equal(a.rejected.length,0);
 assert.deepEqual(a.rows.slice(0,4).map(r=>r.precip_mm),[154.5,134.2,101.9,100.7]);
 assert.equal(a.rows.find(x=>x.name==='استانداری رشت').precip_mm,59.1);
 assert.equal(a.rows.find(x=>x.name==='امامزاده اسحاق').precip_mm,134.2);
 assert.equal(a.rows.at(-1).precip_mm,0);
});
test('exact same county/province synoptic > climatology > raingauge > geographical',()=>{
 const refs=[
  {id:'r',name:'امامزاده اسحاق',province:'گیلان',county:'شفت',lat:37.1,lon:49.2,station_type:'raingauge'},
  {id:'c',name:'امامزاده اسحاق',province:'گیلان',county:'شفت',lat:37.2,lon:49.1,station_type:'climatology'},
  {id:'s',name:'امامزاده اسحاق',province:'گیلان',county:'شفت',lat:37.3,lon:49.3,station_type:'synoptic'},
  {id:'wrong',name:'امامزاده اسحاق',province:'خوزستان',county:'دزفول',lat:32.3,lon:48.3,station_type:'synoptic'}];
 const q={name:'امامزاده اسحاق',province:'گیلان',county:'شفت'};
 assert.equal(M.resolveOne(q,refs).chosen.id,'s');
 assert.equal(M.resolveOne(q,refs.filter(x=>x.id!=='s')).chosen.id,'c');
 assert.equal(M.resolveOne(q,refs.filter(x=>x.id==='r')).chosen.id,'r');
});
test('no wrong-province substitution for Imamzadeh Eshagh',()=>{
 const q={name:'امامزاده اسحاق',province:'گیلان',county:'شفت'};
 assert.equal(M.resolveOne(q,[],[{name:'امامزاده اسحاق',province:'خوزستان',county:'دزفول',lat:32.2,lon:48.1}]).status,'needs_geocoding');
});
test('same-priority same-county homonyms require review',()=>{
 const rows=['a','b'].map(id=>({id,name:'شوییل',province:'گیلان',county:'رودسر',lat:37.1,lon:50.2,station_type:'raingauge'}));
 assert.equal(M.resolveOne({name:'شوییل',province:'گیلان',county:'رودسر'},rows).status,'ambiguous');
});
test('unknown network class is not mislabeled synoptic',()=>{
 const rows=[{id:'x',name:'گیسوم',province:'گیلان',county:'تالش',lat:37.5,lon:49,station_type:'meteorological'}];
 assert.equal(M.resolveOne({name:'گیسوم',province:'گیلان'},rows).status,'review');
});
test('missing longitude is not a valid geographic match',()=>{
 assert.equal(M.resolveOne({name:'کیاشهر',province:'گیلان'},[{name:'کیاشهر',province:'گیلان',lat:37.4,station_type:'synoptic'}]).status,'review');
});
test('auto geocoder only if exact uniquely admin verified, else requires review',async()=>{
 const input=[{name:'امامزاده اسحاق',province:'گیلان',county:'شفت'}];
 const good=await M.resolveBatch(input,[],{geocode:async()=>({status:'exact',lat:37.05,lon:49.11,unique:true,admin_verified:true})});
 assert.equal(good.counts.auto_geographic,1);assert.equal(good.records[0].chosen.not_sensor,true);
 const bad=await M.resolveBatch(input,[],{geocode:async()=>({status:'exact',lat:37.05,lon:49.11,unique:true,admin_verified:false})});
 assert.equal(bad.counts.pending,1);
});
test('all mapped rows can render by default; no hard-coded selection cap',()=>{
 const a=Array.from({length:160},(_,i)=>({status:'auto_station',chosen:{id:i}}));
 assert.deepEqual(M.summary(a),{total:160,auto_station:160,auto_geographic:0,needs_geocoding:0,ambiguous:0,review:0,unresolved:0,invalid:0,mapped:160,pending:0});
});

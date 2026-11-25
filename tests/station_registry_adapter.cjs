const assert=require('node:assert/strict'),fs=require('node:fs');
const {adapt}=require('../station_registry_adapter.js');
const {suggest}=require('../station_name_suggestions.js');
const sample={id:'X',fa:'استهبان',en:'Estahban',ostan:'فارس',lat:29.1,lon:54,type:'synoptic',supports_precip_metadata_join:true};
const r=adapt({stations:[sample,{...sample,id:'Y',requires_review:true},{...sample,id:'Z',lat:''},{...sample,id:'H',type:'hydrometric'},{...sample,id:'N',supports_precip_metadata_join:false}],review_only:[sample]});
assert.equal(r.counts.accepted,1);assert.equal(r.counts.review_only,1);
assert.equal(r.records[0].county,'');assert.equal(r.records[0].province,'فارس');
assert.equal(suggest('Estahbann',r.records)[0].candidate.id,'X');
assert.equal(adapt({stations:[sample,sample]}).counts.accepted,0);
assert.equal(adapt({stations:[{...sample,ostan:''}]}).counts.accepted,0);
assert.throws(()=>adapt({}));
if(process.argv[2]){
 const registry=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const {records,counts}=adapt(registry);
 assert.equal(new Set(records.map(r=>r.id)).size,records.length);
 assert.ok(records.length>0);
 const probes=records.filter(r=>r.nameEn).slice(0,100);
 let found=0,top=0;
 for(const r of probes){const hits=suggest(r.nameEn,records,{province:r.province},30);if(hits.some(x=>x.candidate.id===r.id))found++;if(hits[0]?.candidate.id===r.id)top++;}
 const report={counts,english_exact_self_lookup:{tested:probes.length,within_top_30:found,rank_1:top},note:'Self lookup is a schema and coverage check, not independent recognition accuracy. No private DB accessed.'};
 fs.writeFileSync('station-registry-audit.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(report,null,2));
}else console.log('registry adapter tests passed');

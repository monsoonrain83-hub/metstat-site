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
 function audit(sample,query){
  const metrics={tested:0,within_top_5:0,within_top_30:0,rank_1:0,unique_top_correct:0,ambiguous_top:0,correct_in_top_tie:0,no_candidates:0};
  for(const r of sample){
   const q=query(r);if(!q)continue;
   const hits=suggest(q,records,{province:r.province},30);metrics.tested++;
   if(!hits.length){metrics.no_candidates++;continue;}
   if(hits.slice(0,5).some(x=>x.candidate.id===r.id))metrics.within_top_5++;
   if(hits.some(x=>x.candidate.id===r.id))metrics.within_top_30++;
   if(hits[0].candidate.id===r.id)metrics.rank_1++;
   if(hits[0].topTieCount>1){
    metrics.ambiguous_top++;
    if(hits.some(x=>x.ambiguousTop&&x.candidate.id===r.id))metrics.correct_in_top_tie++;
   }else if(hits[0].candidate.id===r.id)metrics.unique_top_correct++;
  }
  return metrics;
 }
 const fa=records.filter(r=>r.nameFa).slice(0,100);
 const report={counts,english_exact_self_lookup:audit(probes,r=>r.nameEn),persian_exact_self_lookup:audit(fa,r=>r.nameFa),synthetic_english_typo:audit(probes,r=>r.nameEn.length>=5?r.nameEn.slice(0,-1)+r.nameEn.slice(-1).repeat(2):null),synthetic_persian_spacing:audit(fa,r=>r.nameFa.replace(/\s+/g,'')),note:'Self lookup and synthetic perturbations are coverage tests, not independently labeled rainfall reports. Tied names are not errors to resolve by arbitrary ordering. No private DB accessed.'};
 fs.writeFileSync('station-registry-audit.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(report,null,2));
}else console.log('registry adapter tests passed');

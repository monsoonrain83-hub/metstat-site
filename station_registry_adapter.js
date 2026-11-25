/* Read-only adapter for public MetStat atlas station metadata V33.
 * This is not a rainfall eligibility decision and not the private V45 DB.
 * Preserve IDs and existing geographic metadata; never infer county or coordinates. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatStationRegistryAdapter=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const str=v=>typeof v==='string'?v.trim():'';
const numeric=v=>(typeof v==='number'||(typeof v==='string'&&v.trim()!==''))&&Number.isFinite(Number(v));
function adapt(registry){
 if(!registry||!Array.isArray(registry.stations))throw new TypeError('Expected a registry stations array');
 const counts={input:registry.stations.length,review_only:Array.isArray(registry.review_only)?registry.review_only.length:0,excluded:{review:0,unsupported:0,coordinates:0,identity:0,duplicate:0},accepted:0,county:0,english:0};
 const records=[];
 const frequency=new Map();
 for(const r of registry.stations){if(r&&str(r.id))frequency.set(str(r.id),(frequency.get(str(r.id))||0)+1);}
 for(const r of registry.stations){
  if(!r||!str(r.id)||!str(r.ostan)||(!str(r.fa)&&!str(r.en))){counts.excluded.identity++;continue;}
  if(r.requires_review||r.review_status==='review_only'){counts.excluded.review++;continue;}
  if(r.supports_precip_metadata_join!==true||r.rainfall_eligible===false||/hydrometric|hydrology|road|geographic_place/i.test(str(r.type))){counts.excluded.unsupported++;continue;}
  if(!numeric(r.lat)||!numeric(r.lon)||Number(r.lat)<24||Number(r.lat)>41||Number(r.lon)<43||Number(r.lon)>64){counts.excluded.coordinates++;continue;}
  if(frequency.get(str(r.id))!==1){counts.excluded.duplicate++;continue;}
  const record={id:str(r.id),nameFa:str(r.fa),nameEn:str(r.en),province:str(r.ostan),county:str(r.county),city:str(r.city),district:str(r.district),lat:Number(r.lat),lon:Number(r.lon),type:str(r.type),aliases:Array.isArray(r.aliases)?r.aliases.filter(v=>typeof v==='string'):[],metadataOnly:r.metadata_only===true,source:'atlas_registry_v33'};
  records.push(record);
  if(record.county)counts.county++;
  if(record.nameEn)counts.english++;
 }
 counts.accepted=records.length;
 return {records,counts};
}
return Object.freeze({adapt});
});

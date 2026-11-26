const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root='v82-candidate/assets';const core=fs.readFileSync(root+'/'+fs.readdirSync(root).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
const code=core.slice(core.indexOf('async function ms82FetchManifest('),core.indexOf('\nasync function onLoadManifest(){'));
const valid={status:'downloading',models:{ecmwf:{run:'2026112600'}},items:[{m:'ecmwf',r:'iran',p:'t2m',s:24,v:'2026112700'}],items_prev:[{m:'ecmwf',r:'iran',p:'t2m',s:48,v:'2026112700'}],meta:{test:'unchanged'}};
const waiting={status:'waiting',models:[],items:[],items_prev:[],next:'2026112612'};
const tag='W/"'+'a'.repeat(64)+'-0"',tag2='W/"'+'b'.repeat(64)+'-0"';
const response=(status,m,t=tag)=>({status,ok:status>=200&&status<300,headers:{get:()=>t},text:async()=>JSON.stringify(m)});
const good=(m,t=tag)=>response(200,m,t);
function setup(queue){
 const calls=[],timers=new Set();let count=0;
 const ctx=vm.createContext({AbortController,Date,Error,JSON,setTimeout:()=>{timers.add(++count);return count;},clearTimeout:t=>timers.delete(t),fetch:async(url,opts)=>{calls.push({url,cache:opts.cache,headers:opts.headers});const fn=queue.shift();if(!fn)throw Error('unexpected request');return fn();}});
 vm.runInContext(code,ctx);
 return {ctx,calls,timers,run:async()=>{try{return await ctx.ms82FetchManifest('/online/');}finally{assert.equal(timers.size,0);}}};
}
(async()=>{
 let s=setup([()=>good(valid),()=>response(304,null),()=>good(waiting,tag2)]);
 const a=await s.run();assert.deepEqual(a,valid);a.items.length=0;
 assert.deepEqual(await s.run(),valid);assert.equal(s.calls[1].headers['If-None-Match'],tag);
 assert.deepEqual(await s.run(),waiting);assert.equal(s.calls[2].headers['If-None-Match'],tag);
 assert.equal(s.ctx.ms82FetchManifest.cache.tag,tag2);
 for(const call of s.calls){assert.equal(call.url,'/online/model_catalog.php');assert.equal(call.cache,'no-store');}
 s=setup([()=>response(503,null),()=>good(valid,null)]);assert.deepEqual(await s.run(),valid);assert.match(s.calls[1].url,/^\/online\/data\/manifest\.json\?\d+$/);assert.equal(s.ctx.ms82FetchManifest.cache,null);
 s=setup([()=>good(valid,'bad-tag'),()=>good(valid,null)]);assert.deepEqual(await s.run(),valid);
 s=setup([()=>response(304,null),()=>good(valid,null)]);assert.deepEqual(await s.run(),valid);
 s=setup([()=>good(valid),()=>response(304,null,tag2),()=>good(waiting,null)]);await s.run();assert.deepEqual(await s.run(),waiting);assert.equal(s.ctx.ms82FetchManifest.cache,null);
 s=setup([()=>({ok:true,status:200,headers:{get:()=>tag},text:async()=>'{'}),()=>good({models:{},items:{}}),()=>good(valid,null)]);assert.deepEqual(await s.run(),valid);
 s=setup([()=>{throw Error('network');},()=>response(502,null),()=>response(503,null)]);await assert.rejects(s.run());
 console.log('PASS: content hash revalidation, unchanged raw snapshot despite caller mutation, new manifest, invalid validators, missing snapshot, malformed responses, static fallback and failure.');
})().catch(e=>{console.error(e);process.exitCode=1;});

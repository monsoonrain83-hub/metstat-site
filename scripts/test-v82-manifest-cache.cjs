const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root='v82-candidate/assets';const core=fs.readFileSync(root+'/'+fs.readdirSync(root).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
const code=core.slice(core.indexOf('async function ms82FetchManifest('),core.indexOf('\nasync function onLoadManifest(){'));
assert(code.includes('no-cache'));
const valid={status:'downloading',models:{ecmwf:{run:'2026112600'}},items:[{m:'ecmwf',r:'iran',p:'t2m',s:24,v:'2026112700'}],items_prev:[{m:'ecmwf',r:'iran',p:'t2m',s:48,v:'2026112700'}],meta:{test:'unchanged'}};
const waiting={status:'waiting',models:[],items:[],items_prev:[],next:'2026112612'};
const ok=m=>({ok:true,json:async()=>m});
async function scenario(queue,expected){
 const calls=[],timers=new Set();let count=0;
 const ctx=vm.createContext({AbortController,Date,Error,setTimeout:()=>{timers.add(++count);return count;},clearTimeout:t=>timers.delete(t),fetch:async(url,opts)=>{calls.push({url,cache:opts.cache,signal:opts.signal});const fn=queue.shift();if(!fn)throw Error('unexpected request');return fn();}});
 vm.runInContext(code,ctx);
 let result,err;try{result=await ctx.ms82FetchManifest('/online/');}catch(e){err=e;}
 assert.equal(timers.size,0);assert.equal(calls[0].url,'/online/data/manifest.json');assert.equal(calls[0].cache,'no-cache');
 for(const c of calls.slice(1)){assert.match(c.url,/^\/online\/data\/manifest\.json\?\d+$/);assert.equal(c.cache,'no-store');}
 if(expected===null)assert(err);else{assert.ifError(err);assert.deepEqual(result,expected);}
 return calls.length;
}
(async()=>{
 assert.equal(await scenario([()=>ok(valid)],valid),1);
 assert.equal(await scenario([()=>ok(waiting)],waiting),1);
 assert.equal(await scenario([()=>({ok:false,status:503}),()=>ok(valid)],valid),2);
 assert.equal(await scenario([()=>({ok:true,json:async()=>{throw Error('invalid JSON');}}),()=>ok(valid)],valid),2);
 assert.equal(await scenario([()=>ok({status:'fake'}),()=>ok({models:{},items:{}}),()=>ok(valid)],valid),3);
 assert.equal(await scenario([()=>{throw Error('network');},()=>ok({models:{},items:[],items_prev:{}}),()=>ok(valid)],valid),3);
 assert.equal(await scenario([()=>({ok:false,status:500}),()=>({ok:false,status:502}),()=>({ok:false,status:503})],null),3);
 console.log('7 manifest tests passed: unchanged full schema, waiting, errors, fallback, timer cleanup and failure.');
})().catch(e=>{console.error(e);process.exitCode=1;});

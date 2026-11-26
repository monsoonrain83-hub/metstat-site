// Read-only CPU attribution on the public homepage, no trace payload or cookies retained.
const {chromium}=require('playwright');
const fs=require('node:fs'),crypto=require('node:crypto');
const BASE='https://wtafkik.ir';
const expected={index:'adf50bd8e9a2f0402d9b33acfb44cda8dfd236ae22d268c9adf94f8fc306e362',core:'eca95cc1c84b0ff52374230abb0c03cf2802e10fe706173dd872746b6c7cd1e0'};
function summarize(profile){
 const nodes=new Map(profile.nodes.map(n=>[n.id,n.callFrame]));
 const totals=new Map();let sampleMs=0,nonIdleMs=0;
 for(let i=0;i<(profile.samples||[]).length;i++){
  const f=nodes.get(profile.samples[i]);const us=profile.timeDeltas?.[i];
  if(!f||!Number.isFinite(us)||us<0)continue;
  const ms=us/1000;sampleMs+=ms;
  if(f.functionName==='(idle)')continue;nonIdleMs+=ms;
  let file='runtime';
  try{const u=new URL(f.url);if(u.origin===BASE)file=u.pathname;else if(f.url)file='other';}catch{if(f.url)file='other';}
  const name=(f.functionName||'(anonymous)').slice(0,100);
  const line=(Number.isInteger(f.lineNumber)&&f.lineNumber>=0)?f.lineNumber+1:null;
  const key=JSON.stringify([file,name,line]);
  totals.set(key,(totals.get(key)||0)+ms);
 }
 const hot=[...totals].sort((a,b)=>b[1]-a[1]).slice(0,30).map(([k,ms])=>{const [file,name,line]=JSON.parse(k);return {file,name,line,selfSampleMs:Math.round(ms)}});
 return {sampleMs:Math.round(sampleMs),nonIdleMs:Math.round(nonIdleMs),hot};
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 const reports=[];
 try{
  for(const p of [{name:'desktop',viewport:{width:1440,height:900}},{name:'touch',viewport:{width:390,height:844},hasTouch:true,isMobile:true}]){
   const {name,...opts}=p;
   const ctx=await browser.newContext({...opts,serviceWorkers:'block'});
   await ctx.route('**/*',route=>{
    const req=route.request(),u=new URL(req.url());
    if(['data:','blob:'].includes(u.protocol))return route.continue();
    if(u.origin!==BASE||!['GET','HEAD'].includes(req.method()))return route.abort();
    if(u.pathname.startsWith('/admin/')||u.pathname.startsWith('/auth_data/'))return route.abort();
    return route.continue();
   });
   const page=await ctx.newPage(),cdp=await ctx.newCDPSession(page);
   const report={profile:name};reports.push(report);
   try{
    await cdp.send('Profiler.enable');
    await cdp.send('Profiler.setSamplingInterval',{interval:1000});
    await cdp.send('Profiler.start');
    const corePromise=page.waitForResponse(r=>r.ok()&&new URL(r.url()).origin===BASE&&/\/assets\/ms_r5_perf_core_[a-f0-9]+\.js$/.test(new URL(r.url()).pathname),{timeout:45000});
    const res=await page.goto(BASE+'/',{waitUntil:'domcontentloaded',timeout:45000});
    if(!res?.ok())throw Error('home response failed');
    const core=await corePromise;
    const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
    report.hashes={index:hash(await res.body()),core:hash(await core.body())};
    report.matchesV82=Object.keys(expected).every(k=>report.hashes[k]===expected[k]);
    await page.waitForTimeout(10000);
    const result=await cdp.send('Profiler.stop');Object.assign(report,summarize(result.profile));
    report.resources=await page.evaluate(()=>{
     const a=performance.getEntriesByType('resource').filter(e=>{try{return new URL(e.name).origin===location.origin}catch{return false}});
     return a.map(e=>({path:new URL(e.name).pathname,transferBytes:e.transferSize,decodedBytes:e.decodedBodySize,durationMs:Math.round(e.duration)})).sort((a,b)=>b.decodedBytes-a.decodedBytes).slice(0,20);
    });
    report.status='ok';
   }catch(e){report.status='failed';report.error=String(e.message).slice(0,180);}
   finally{await ctx.close();}
  }
 }finally{
  await browser.close();
  fs.writeFileSync('metstat-cpu-profile.json',JSON.stringify({measuredAt:new Date().toISOString(),note:'CDP sampled self time; not total inclusive duration, Lighthouse or field data. No raw trace retained.',reports},null,2));
 }
 if(reports.some(r=>r.status!=='ok'))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});

// Read-only first-party performance baseline. Not a Lighthouse score.
const {chromium}=require('playwright');
const fs=require('node:fs');
const crypto=require('node:crypto');
const BASE='https://wtafkik.ir';
const profiles=[{name:'desktop',viewport:{width:1440,height:900},touch:false},{name:'touch',viewport:{width:390,height:844},touch:true}];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const reports=[];
 try {
  for(const p of profiles){
   const ctx=await browser.newContext({viewport:p.viewport,hasTouch:p.touch,isMobile:p.touch,serviceWorkers:'block'});
   let blocked=0; const failed=[],errors=[],hashes={};
   await ctx.route('**/*',route=>{
    const req=route.request();const u=new URL(req.url());
    if(u.protocol==='data:'||u.protocol==='blob:')return route.continue();
    if(u.origin!==BASE||!['GET','HEAD'].includes(req.method())){blocked++;return route.abort();}
    return route.continue();
   });
   await ctx.addInitScript(()=>{
    const m=window.__msPerf={lcp:null,longTasks:[],observed:[]};
    for(const type of ['largest-contentful-paint','longtask']){
     try{const o=new PerformanceObserver(list=>{for(const e of list.getEntries()){if(type==='longtask')m.longTasks.push({start:e.startTime,duration:e.duration});else m.lcp=e.startTime;}});o.observe({type,buffered:true});m.observed.push(type);}catch{}
    }
   });
   const page=await ctx.newPage();
   page.on('pageerror',e=>{errors.push(String(e.name||'Error'));});
   page.on('requestfailed',req=>{const u=new URL(req.url());if(u.origin===BASE)failed.push({path:u.pathname,error:req.failure()?.errorText});});
   const pending=[];
   page.on('response',r=>{
    const u=new URL(r.url());
    if(u.origin!==BASE||!r.ok()||!(r.request().resourceType()==='document'||/\/assets\/ms_r5_perf_core_[a-f0-9]+\.js$/.test(u.pathname)))return;
    pending.push(r.body().then(b=>{hashes[u.pathname]={sha256:crypto.createHash('sha256').update(b).digest('hex'),bytes:b.length};}).catch(()=>{}));
   });
   try {
    const resp=await page.goto(BASE+'/',{waitUntil:'domcontentloaded',timeout:45000});
    if(!resp||!resp.ok())throw Error('Home response not successful');
    await page.waitForTimeout(10000);
    const data=await page.evaluate(()=>{
     const nav=performance.getEntriesByType('navigation')[0],m=window.__msPerf;
     const resources=performance.getEntriesByType('resource').filter(e=>{try{return new URL(e.name).origin===location.origin}catch{return false}});
     const list=resources.map(e=>({path:new URL(e.name).pathname,type:e.initiatorType,startMs:Math.round(e.startTime),durationMs:Math.round(e.duration),transferBytes:e.transferSize,encodedBytes:e.encodedBodySize,decodedBytes:e.decodedBodySize}));
     return {elapsedMs:Math.round(performance.now()),ttfbMs:nav?.responseStart??null,domContentLoadedMs:nav?.domContentLoadedEventEnd??null,loadMs:nav?.loadEventEnd??null,fcpMs:performance.getEntriesByName('first-contentful-paint')[0]?.startTime??null,lcpObservedMs:m.lcp,longTaskCount:m.longTasks.length,longTaskBlockingEstimateMs:m.observed.includes('longtask')?Math.round(m.longTasks.reduce((n,t)=>n+Math.max(0,t.duration-50),0)):null,observed:m.observed,resourceCount:list.length,transferBytes:list.reduce((n,e)=>n+e.transferBytes,0),decodedBytes:list.reduce((n,e)=>n+e.decodedBytes,0),largest:list.sort((a,b)=>b.decodedBytes-a.decodedBytes).slice(0,20),overlayRequests:list.filter(e=>/wu_zoom_overlays|tt_me_overlay/.test(e.path)),manifestRequests:list.filter(e=>e.path==='/online/data/manifest.json').length};
    });
    await Promise.allSettled(pending);
    reports.push({profile:p.name,status:resp.status,firstPartyOnly:true,...data,hashes,blockedRequests:blocked,failed:failed.slice(0,40),pageErrorCount:errors.length});
   }catch(e){reports.push({profile:p.name,error:String(e.message).slice(0,200),blockedRequests:blocked,hashes});}
   finally {await ctx.close();}
  }
 }finally{await browser.close();fs.writeFileSync('metstat-live-performance.json',JSON.stringify({measuredAt:new Date().toISOString(),note:'Synthetic cold browser, first-party GET/HEAD only, 10-second observation after DOMContentLoaded; not field data or Lighthouse TBT.',reports},null,2));}
 if(reports.some(r=>r.error))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});

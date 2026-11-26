// Verify V81 against the same live V80 origin, replacing only two responses.
// No POST requests, credentials, private URLs, or host changes.
const {chromium}=require('playwright');
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const BASE='https://wtafkik.ir', root='v81-candidate';
const old='/assets/ms_r5_perf_core_5bf9868a04910eee.js';
const name=fs.readdirSync(root+'/assets').find(x=>/^ms_r5_perf_core_[a-f0-9]+\.js$/.test(x));
assert(name);
const index=fs.readFileSync(root+'/index.html'),core=fs.readFileSync(root+'/assets/'+name);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const BASE_INDEX='4aacde5aaf85930180453c91c915791c21d848ee3abae145acd086029fd9a8db';
const BASE_CORE='5bf9868a04910eee68c29c37f8a701932fd1c9f11c55c805d79234539f190c8a';
const overlays=/\/assets\/(?:wu_zoom_overlays|tt_me_overlay)\.js$/;
const reports=[];
(async()=>{
 const browser=await chromium.launch();
 try{
  for(const profile of [{name:'desktop',viewport:{width:1440,height:900}},{name:'touch',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]){
   for(const candidate of [false,true]){
    const {name:profileName,...contextOptions}=profile;
    const ctx=await browser.newContext({...contextOptions,serviceWorkers:'block'});
    const page=await ctx.newPage(),requests=[],errors=[],failures=[];
    const report={profile:profile.name,candidate};
    reports.push(report);
    try{
     await ctx.route('**/*',async route=>{
      const req=route.request(),u=new URL(req.url());
      if(['data:','blob:'].includes(u.protocol))return route.continue();
      if(u.origin!==BASE||!['GET','HEAD'].includes(req.method()))return route.abort();
      if(candidate&&u.pathname==='/'&&req.resourceType()==='document')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:index});
      if(candidate&&u.pathname==='/assets/'+name)return route.fulfill({status:200,contentType:'application/javascript; charset=utf-8',body:core});
      return route.continue();
     });
     page.on('request',req=>{const u=new URL(req.url());if(u.origin===BASE&&overlays.test(u.pathname))requests.push(u.pathname);});
     page.on('pageerror',e=>errors.push(String(e.message).slice(0,150)));
     page.on('requestfailed',req=>{const u=new URL(req.url());if(u.origin===BASE&&overlays.test(u.pathname))failures.push(u.pathname);});
     await ctx.addInitScript(()=>{
      window.__v81perf={lcp:null,long:[]};
      try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__v81perf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch{}
      try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__v81perf.long.push(e.duration);}).observe({type:'longtask',buffered:true});}catch{}
     });
     const original=page.waitForResponse(r=>new URL(r.url()).pathname===(candidate?'/assets/'+name:old)&&r.ok(),{timeout:45000});
     const res=await page.goto(BASE+'/',{waitUntil:'domcontentloaded',timeout:45000});
     assert(res&&res.ok());
     assert.equal(sha(await res.body()),candidate?sha(index):BASE_INDEX,'unexpected HTML baseline');
     assert.equal(sha(await (await original).body()),candidate?sha(core):BASE_CORE,'unexpected JS baseline');
     await page.waitForFunction(()=>typeof wuZoomsReady==='function'&&typeof ttOvLoad==='function'&&typeof wuzRefresh==='function',null,{timeout:20000});
     await page.waitForTimeout(10000);
     await page.waitForFunction(()=>typeof NV!=='undefined'&&NV.entry?.img?.complete&&NV.entry.img.naturalWidth>0,null,{timeout:20000});
     report.initial=await page.evaluate(()=>{
      const res=performance.getEntriesByType('resource');
      const data=res.filter(e=>{try{return new URL(e.name).origin===location.origin}catch{return false}});
      return {resources:data.length,decodedBytes:data.reduce((n,e)=>n+e.decodedBodySize,0),transferBytes:data.reduce((n,e)=>n+e.transferSize,0),lcpMs:window.__v81perf.lcp,blockingEstimateMs:Math.round(window.__v81perf.long.reduce((n,x)=>n+Math.max(0,x-50),0)),mapImages:(typeof NV!=='undefined'&&NV.entry?.img?.complete&&NV.entry.img.naturalWidth>0&&document.getElementById('nvCv')?.width>0)?1:0,route:location.pathname};
     });
     report.initialOverlayRequests=requests.slice();
     report.initialErrors=errors.slice();
     if(candidate){
      assert.equal(requests.length,0,'optional bundles requested at startup');
      const results=await page.evaluate(async()=>{
       await Promise.all([wuZoomsReady(),wuZoomsReady(),ttOvLoad(),ttOvLoad()]);
       return {wu:Object.values(WU_ZOOM_IMG).filter(x=>x.complete&&x.naturalWidth>0).length,tt:TT_OV_IMG.naturalWidth};
      });
      report.onDemand=results;
      report.onDemandRequests=requests.slice();
      assert(results.wu>0&&results.tt>0,'overlay images did not decode');
      assert.equal(requests.filter(x=>x.includes('wu_zoom')).length,1);
      assert.equal(requests.filter(x=>x.includes('tt_me')).length,1);
      assert.equal(failures.length,0,'overlay requests failed');
     }else{
      assert(requests.some(x=>x.includes('wu_zoom'))&&requests.some(x=>x.includes('tt_me')),'baseline did not reproduce startup requests');
     }
     report.errors=errors.slice();
     report.status='pass';
    }catch(e){report.status='fail';report.failure=String(e.message).slice(0,500);report.requests=requests.slice();report.errors=errors.slice();throw e;}
    finally{await ctx.close();}
   }
   const [base,next]=reports.filter(x=>x.profile===profile.name);
   assert.equal(next.initial.route,base.initial.route,'navigation regression');
   assert(next.initial.mapImages>=1&&base.initial.mapImages>=1,'initial model map not confirmed');
   assert(next.errors.every(e=>base.errors.includes(e)),'new browser errors');
  }
 }finally{
  fs.writeFileSync('v81-browser-report.json',JSON.stringify({measuredAt:new Date().toISOString(),reports,note:'Only first-party GET/HEAD. Candidate HTML/JS fulfilled locally in browser; transfer bytes not directly comparable. No actual user export test.'},null,2));
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1;});

// Verify V81 against the same live V80 origin, replacing only two responses.
// No POST requests, credentials, private URLs, or host changes.
const {chromium}=require('playwright');
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const BASE='https://wtafkik.ir', root='v85-candidate';
const old='/assets/ms_r5_perf_core_eca95cc1c84b0ff5.js';
const name=fs.readdirSync(root+'/assets').find(x=>/^ms_r5_perf_core_[a-f0-9]+\.js$/.test(x));
assert(name);
const index=fs.readFileSync(root+'/index.html'),core=fs.readFileSync(root+'/assets/'+name);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const BASE_INDEX='adf50bd8e9a2f0402d9b33acfb44cda8dfd236ae22d268c9adf94f8fc306e362';
const BASE_CORE='eca95cc1c84b0ff52374230abb0c03cf2802e10fe706173dd872746b6c7cd1e0';
const overlays=/\/assets\/(?:wu_zoom_overlays|tt_me_overlay)\.js$/;
const reports=[];
const manifest=fs.readFileSync('v85-manifest.json');
const tag='W/"'+sha(manifest)+'-0"';
(async()=>{
 const browser=await chromium.launch();
 try{
  for(const profile of [{name:'desktop',viewport:{width:1440,height:900}},{name:'touch',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]){
   for(const candidate of [false,true]){
    const {name:profileName,...contextOptions}=profile;
    const ctx=await browser.newContext({...contextOptions,serviceWorkers:'block'});
    const page=await ctx.newPage(),requests=[],errors=[],failures=[],manifestRequests=[];
    const report={profile:profile.name,candidate};
    reports.push(report);
    try{
     await ctx.route('**/*',async route=>{
      const req=route.request(),u=new URL(req.url());
      if(['data:','blob:'].includes(u.protocol))return route.continue();
      if(u.origin!==BASE||!['GET','HEAD'].includes(req.method()))return route.abort();
      if(['/online/model_catalog.php','/online/data/manifest.json'].includes(u.pathname)){
       if(req.headers()['if-none-match']===tag) return route.fulfill({status:304,headers:{etag:tag}});
       return route.fulfill({status:200,contentType:'application/json',headers:{etag:tag},body:manifest});
      }
      if(candidate&&u.pathname==='/'&&req.resourceType()==='document')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:index});
      if(candidate&&u.pathname==='/assets/'+name)return route.fulfill({status:200,contentType:'application/javascript; charset=utf-8',body:core});
      return route.continue();
     });
     page.on('request',req=>{const u=new URL(req.url());if(u.origin===BASE&&overlays.test(u.pathname))requests.push(u.pathname);if(u.origin===BASE&&['/online/data/manifest.json','/online/model_catalog.php'].includes(u.pathname))manifestRequests.push(u.pathname+u.search);});
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
     report.manifestRequests=manifestRequests.slice();
     if(candidate)assert(manifestRequests.includes('/online/model_catalog.php'),'stable catalog URL not used');
     report.initialErrors=errors.slice();
     assert.equal(requests.length,0,'optional bundles requested at startup');
     const ready=()=>page.waitForFunction(()=>!NV.busy&&NV.entry?.item?.v===NV.s.fr&&NV.entry?.item?.m===NV.s.m&&NV.entry?.img?.naturalWidth>0,null,{timeout:25000});
     const state=()=>page.evaluate(()=>({m:NV.s.m,p:NV.s.p,fr:NV.s.fr,run:nvRunSel(NV.s.m),file:NV.entry.item.f,models:nvModelsOf(NV.s.tc).map(([k])=>k),frames:NV.items.map(i=>i.v)}));
     const timed=async(fn)=>{const t=Date.now();await fn();await ready();return Date.now()-t;};
     report.states=[await state()];
     report.interactionMs=[];
     assert(await page.locator('#nvFr option').count()>1,'need multiple forecast frames');
     report.interactionMs.push(await timed(()=>page.locator('#nvNext').click()));
     report.states.push(await state());assert.notEqual(report.states[1].fr,report.states[0].fr);
     report.interactionMs.push(await timed(()=>page.locator('#nvPrev').click()));
     report.states.push(await state());assert.equal(report.states[2].fr,report.states[0].fr);
     const chip=page.locator('#nvBar button[data-m]:not(.on)').first();
     if(await chip.count()){
      report.interactionMs.push(await timed(()=>chip.click()));report.states.push(await state());assert.notEqual(report.states.at(-1).m,report.states[0].m);
     }
     const alt=page.locator('#nvWx button[data-p]:not(.on):not([disabled])').first();
     if(await alt.isVisible()){
      const before=report.states.at(-1).p;report.interactionMs.push(await timed(()=>alt.click()));report.states.push(await state());assert.notEqual(report.states.at(-1).p,before);
     }
     // Compare selected frames, model list and run; timings are observational.
     // Exercise the real model-map download function, not a synthetic canvas.
     const downloadPromise=page.waitForEvent('download',{timeout:30000});
     await page.evaluate(()=>nvExport(900));
     const download=await downloadPromise;
     assert.equal(await download.failure(),null,'PNG export failed');
     const file=await download.path();
     const png=fs.readFileSync(file);
     assert(png.length>1000&&png.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])),'invalid PNG');
     const width=png.readUInt32BE(16),height=png.readUInt32BE(20);
     assert(width>=900&&height>=400&&width<=1200&&height<=4000,'unexpected PNG dimensions');
     assert(download.suggestedFilename().endsWith('.png'),'unexpected download format');
     report.png={width,height,bytes:png.length,filename:download.suggestedFilename()};
     if(candidate){
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
      assert.equal(requests.length,0,'V82 baseline overlay startup regression');
     }
     report.errors=errors.slice();
     report.status='pass';
    }catch(e){report.status='fail';report.failure=String(e.message).slice(0,500);report.requests=requests.slice();report.errors=errors.slice();throw e;}
    finally{await ctx.close();}
   }
   const [base,next]=reports.filter(x=>x.profile===profile.name);
   assert.equal(next.initial.route,base.initial.route,'navigation regression');
   assert.deepEqual(next.states,base.states,'model/frame selection regression');
   assert(next.initial.mapImages>=1&&base.initial.mapImages>=1,'initial model map not confirmed');
   assert(next.errors.every(e=>base.errors.includes(e)),'new browser errors');
  }
 }finally{
  fs.writeFileSync('v85-browser-report.json',JSON.stringify({measuredAt:new Date().toISOString(),reports,note:'Only first-party GET/HEAD. Same captured public manifest replayed to both variants; candidate HTML/JS fulfilled in browser; timings are observational. Real online-model PNG download exercised; Weather.us/Tropical Tidbits custom exports still not covered.'},null,2));
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1;});

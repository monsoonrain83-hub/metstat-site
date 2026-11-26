// Replay exact approved V88 and V89 against the same public manifest and assets.
// No POST requests, credentials, private URLs, or host changes.
const {chromium}=require('playwright');
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const BASE='https://wtafkik.ir', root='v89-candidate';
const old='/assets/ms_r5_perf_core_e8ff91ddd6acd959.js';
const name=fs.readdirSync(root+'/assets').find(x=>/^ms_r5_perf_core_[a-f0-9]+\.js$/.test(x));
assert(name);
const index=fs.readFileSync(root+'/index.html'),core=fs.readFileSync(root+'/assets/'+name);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const BASE_INDEX='52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6';
const BASE_CORE='e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040';
const baselineIndex=fs.readFileSync('v89-baseline/index.html'),baselineCore=fs.readFileSync('v89-baseline'+old);
const overlays=/\/assets\/(?:wu_zoom_overlays|tt_me_overlay)\.js$/;
const reports=[];
const manifest=fs.readFileSync('v89-manifest.json');
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
      if(u.pathname==='/'&&req.resourceType()==='document')return route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:candidate?index:baselineIndex});
      if(!candidate&&u.pathname===old)return route.fulfill({status:200,contentType:'application/javascript; charset=utf-8',body:baselineCore});
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
     const ready=()=>page.waitForFunction(()=>!NV.busy&&NV.entry?.item?.v===NV.s.fr&&NV.entry?.item?.m===NV.s.m&&NV.entry?.item?.p===nvPid()&&NV.entry?.img?.naturalWidth>0,null,{timeout:25000});
     const state=()=>page.evaluate(()=>({m:NV.s.m,p:NV.s.p,fr:NV.s.fr,run:nvRunSel(NV.s.m),file:NV.entry.item.f,models:nvModelsOf(NV.s.tc).map(([k])=>k),frames:NV.items.map(i=>i.v)}));
     const timed=async(fn)=>{const t=Date.now();await fn();await ready();return Date.now()-t;};
     report.states=[await state()];
     report.interactionMs=[];
     assert(await page.locator('#nvFr option').count()>1,'need multiple forecast frames');
     report.interactionMs.push(await timed(()=>page.locator('#nvNext').click()));
     report.states.push(await state());assert.notEqual(report.states[1].fr,report.states[0].fr);
     report.interactionMs.push(await timed(()=>page.locator('#nvPrev').click()));
     report.states.push(await state());assert.equal(report.states[2].fr,report.states[0].fr);
     // Select by the actual model key, not a presentation class which other
     // compatibility layers can change. Wait for the requested state before
     // accepting a ready image (the previous frame can still be ready).
     const target=await page.evaluate(()=>[...document.querySelectorAll('#nvBar button[data-m]')].find(b=>!b.disabled&&b.dataset.m!==NV.s.m&&b.getClientRects().length)?.dataset.m);
     assert(target,'no visible alternative model button');
     report.targetModel=target;
     const chip=page.locator('#nvBar button[data-m="'+target+'"]:visible').first();
     report.modelButtons=await page.locator('#nvBar button[data-m]').evaluateAll(bs=>bs.map(b=>({key:b.dataset.m,active:b.classList.contains('on'),visible:!!b.getClientRects().length})));
     await page.evaluate(()=>{window.__ms85ClickEvents=[];for(const t of ['pointerdown','pointerup','click'])document.addEventListener(t,e=>{const x=e.target.closest?.('button[data-m],#nvBar');if(x)window.__ms85ClickEvents.push({type:t,key:x.dataset.m||null,id:x.id,connected:x.isConnected});},true);});
     try{
       report.interactionMs.push(await timed(async()=>{await chip.click();await page.waitForFunction(m=>NV.s.m===m,target,{timeout:10000});}));
       report.modelClick='pass';
     }catch(e){
       report.modelClick='fail';report.modelClickError=String(e.message).slice(0,200);
       report.clickEvents=await page.evaluate(()=>window.__ms85ClickEvents);
       throw e;
     }
     report.clickEvents=await page.evaluate(()=>window.__ms85ClickEvents);
     report.states.push(await state());assert.equal(report.states.at(-1).m,target);
     // R5 replaced the legacy hidden nvWx panel. Exercise the visible
     // canonical parameter picker rather than the compatibility DOM.
     const section=page.locator('button[data-r5section="parameters"]:visible').first();
     await section.waitFor({state:'visible',timeout:15000});
     if(await section.getAttribute('aria-expanded')!=='true')await section.click();
     const picker=page.locator('#msR5ParamPicker');
     await picker.waitFor({state:'visible',timeout:10000});
     const before=await page.evaluate(()=>NV.s.p);
     const findParam=()=>page.evaluate(()=>[...document.querySelectorAll('#msR5ParamPicker button[data-r5param]')].find(b=>!b.disabled&&b.dataset.r5param!==NV.s.p&&b.getClientRects().length)?.dataset.r5param);
     let param=await findParam();
     if(!param){
       const group=picker.locator('button[data-r5group][aria-expanded="false"]:visible').first();
       await group.click();
       param=await findParam();
     }
     assert(param&&param!==before,'R5 alternate parameter must be available');
     report.targetParameter=param;
     const alt=picker.locator('button[data-r5param="'+param+'"]:visible').first();
     report.interactionMs.push(await timed(async()=>{await alt.click();await page.waitForFunction(p=>NV.s.p===p,param,{timeout:10000});}));
     report.states.push(await state());assert.equal(report.states.at(-1).p,param);
     // Same-state forced sync must no longer replace current controls.
     // Measure synchronously to isolate nvrSync from unrelated background jobs.
     report.sidebarSync=await page.evaluate(()=>{
      const hosts=[document.querySelector('#msR5ParamPicker'),document.querySelector('#msR5ModelRows'),document.querySelector('#onAside .msR5-periods'),...document.querySelectorAll('#onAside select[data-mir],.nvCard select[data-mir]'),document.getElementById('nvX5')].filter(Boolean);
      const unique=[...new Set(hosts)];
      nvrSync(true);
      const nodes=unique.map(x=>x.firstElementChild);
      const button=document.querySelector('#msR5ParamPicker button[data-r5param]');
      if(!button)throw Error('parameter control missing');
      button.focus();
      const observer=new MutationObserver(()=>{});
      for(const host of unique)observer.observe(host,{childList:true,subtree:true});
      const t=performance.now();
      for(let i=0;i<10;i++)nvrSync(true);
      const elapsed=performance.now()-t,mutations=observer.takeRecords().length;observer.disconnect();
      return {mutations,elapsedMs:elapsed,stable:unique.every((x,i)=>x.firstElementChild===nodes[i]),focus:document.activeElement===button,hosts:unique.length};
     });
     assert.equal(report.sidebarSync.mutations,0,'unchanged sidebar rewrote DOM');assert(report.sidebarSync.stable,'sidebar node identity changed');assert(report.sidebarSync.focus,'parameter focus lost');
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
     report.png={width,height,bytes:png.length,sha256:sha(png),filename:download.suggestedFilename()};
     // Two real forecast images through the existing GIF encoder, at the lowest
     // supported export width. Do not synthesize success or skip absent frames.
     assert(await page.locator('#nvGf option').count()>=2,'GIF requires two frames');
     await page.evaluate(()=>{document.getElementById('nvGf').value='0';document.getElementById('nvGt').value='1';const w=document.getElementById('nvGw');const opt=[...w.options].sort((a,b)=>Number(a.value)-Number(b.value))[0];if(opt)w.value=opt.value;});
     const gifDownload=page.waitForEvent('download',{timeout:90000});
     await page.evaluate(()=>nvGif());
     const gif=await gifDownload;assert.equal(await gif.failure(),null);
     const g=fs.readFileSync(await gif.path());assert(/^GIF8[79]a$/.test(g.subarray(0,6).toString())&&g.length>1000&&g.at(-1)===0x3b,'invalid GIF');
     report.gif={width:g.readUInt16LE(6),height:g.readUInt16LE(8),bytes:g.length};
     // Frame playback stress: repeated real next/previous clicks, verify
     // final state and that no stale resolve overwrites the selected frame.
     for(let i=0;i<3;i++){await timed(()=>page.locator('#nvNext').click());await timed(()=>page.locator('#nvPrev').click());}
     assert.deepEqual(await state(),report.states.at(-1),'frame roundtrip mismatch');
     if(candidate){report.cache=await page.evaluate(()=>NV_IMAGE_CACHE.stats());assert(report.cache.estimatedBytes<=64*1024*1024&&report.cache.entries<=60);}

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
      assert.equal(requests.length,0,'V87 baseline overlay startup regression');
     }
     report.errors=errors.slice();
     report.status='pass';
    }catch(e){report.status='fail';report.failure=String(e.message).slice(0,500);report.requests=requests.slice();report.errors=errors.slice();throw e;}
    finally{await ctx.close();}
   }
   const [base,next]=reports.filter(x=>x.profile===profile.name);
   assert.equal(next.initial.route,base.initial.route,'navigation regression');
   assert.deepEqual(next.states,base.states,'model/frame selection regression');
   assert.equal(base.modelClick,'pass');assert.equal(next.modelClick,'pass');assert.deepEqual([next.gif.width,next.gif.height],[base.gif.width,base.gif.height],'GIF dimensions regression');assert(base.targetParameter&&next.targetParameter,'both must test parameter click');
   assert(next.initial.mapImages>=1&&base.initial.mapImages>=1,'initial model map not confirmed');
   assert(next.errors.every(e=>base.errors.includes(e)),'new browser errors');
   assert.equal(next.png.sha256,base.png.sha256,'PNG bytes differ');
  }
 }finally{
  fs.writeFileSync('v89-browser-report.json',JSON.stringify({measuredAt:new Date().toISOString(),reports,note:'Only first-party GET/HEAD. Same captured public manifest replayed to both variants; both exact baseline and candidate HTML/JS fulfilled in browser; timings are observational. Real online-model PNG download exercised; Weather.us/Tropical Tidbits custom exports still not covered.'},null,2));
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1;});

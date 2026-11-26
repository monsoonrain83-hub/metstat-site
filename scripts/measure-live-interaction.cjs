// Read-only live gate: no host writes, no private data, no replay.
const {chromium}=require('playwright');
const fs=require('node:fs'), crypto=require('node:crypto'), assert=require('node:assert/strict');
const BASE='https://wtafkik.ir';
const expected={
 V87:['0adaeabb312653692ba463a0bc6c0d24e19a79d9c125ed53aed59eea809ed785','4a4e77930c1b17d3fc39353d32d3c88ac9691edb69d108f84718c1ae49eb239e'],
 V88:['52012e1fd5ff0921dbc49823b311b062752dfd3ac17dbbe46503e438587836e6','e8ff91ddd6acd9597556fb17c60e4ffec6d816c3302bfdd3bde2faf455dda040']
};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function summarize(p){
 const nodes=new Map(p.nodes.map(n=>[n.id,n.callFrame])), totals=new Map();
 for(let i=0;i<(p.samples||[]).length;i++){
  const f=nodes.get(p.samples[i]),us=p.timeDeltas?.[i];
  if(!f||!Number.isFinite(us)||us<0||f.functionName==='(idle)')continue;
  let path='runtime';try{const u=new URL(f.url);path=u.origin===BASE?u.pathname:'other';}catch{}
  const key=JSON.stringify([path,(f.functionName||'(anonymous)').slice(0,100),f.lineNumber+1]);
  totals.set(key,(totals.get(key)||0)+us/1000);
 }
 return [...totals].sort((a,b)=>b[1]-a[1]).slice(0,25).map(([k,v])=>({frame:JSON.parse(k),selfSampleMs:Math.round(v)}));
}
(async()=>{
 const browser=await chromium.launch(),reports=[];
 try{
 for(const profile of [{name:'desktop',viewport:{width:1440,height:900}},{name:'touch',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]){
  const {name,...options}=profile,ctx=await browser.newContext({...options,serviceWorkers:'block'});
  const report={profile:name,interactions:[],errors:0};reports.push(report);
  try{
   await ctx.route('**/*',r=>{
    const q=r.request(),u=new URL(q.url());
    if(['data:','blob:'].includes(u.protocol))return r.continue();
    if(u.origin!==BASE||!['GET','HEAD'].includes(q.method())||/^\/(admin|auth_data|metstat_data)(\/|$)/.test(u.pathname))return r.abort();
    return r.continue();
   });
   await ctx.addInitScript(()=>{
    window.__msLive={tasks:[],events:[],lcp:null,supported:[]};
    for(const type of ['longtask','event','largest-contentful-paint'])try{
     const o=new PerformanceObserver(l=>{for(const e of l.getEntries()){
      const m=window.__msLive;
      if(type==='longtask')m.tasks.push({start:e.startTime,ms:e.duration});
      else if(type==='event'&&e.interactionId)m.events.push({id:e.interactionId,start:e.startTime,ms:e.duration});
      else if(type==='largest-contentful-paint')m.lcp=e.startTime;
     }});o.observe({type,buffered:true,...(type==='event'?{durationThreshold:16}:{})});window.__msLive.supported.push(type);
    }catch{}
   });
   const page=await ctx.newPage(),cdp=await ctx.newCDPSession(page);
   page.on('pageerror',()=>report.errors++);
   await cdp.send('Profiler.enable');
   const core=page.waitForResponse(r=>r.ok()&&new URL(r.url()).origin===BASE&&/\/assets\/ms_r5_perf_core_[a-f0-9]+\.js$/.test(new URL(r.url()).pathname),{timeout:45000});
   const home=await page.goto(BASE+'/',{waitUntil:'domcontentloaded',timeout:45000});
   assert(home?.ok(),'home HTTP failure');
   report.hashes=[sha(await home.body()),sha(await (await core).body())];
   report.version=Object.keys(expected).find(k=>expected[k].every((v,i)=>v===report.hashes[i]))||'UNKNOWN';
   assert.notEqual(report.version,'UNKNOWN','unrecognized live version; stop before testing');
   await page.waitForFunction(()=>typeof NV!=='undefined'&&NV.entry?.img?.naturalWidth>0,null,{timeout:45000});
   const ready=()=>page.waitForFunction(()=>!NV.busy&&NV.entry?.item?.v===NV.s.fr&&NV.entry?.item?.m===NV.s.m&&NV.entry?.item?.p===nvPid()&&NV.entry?.img?.naturalWidth>0,null,{timeout:30000});
   await ready();
   report.startup=await page.evaluate(()=>({lcp:__msLive.lcp,tasks:__msLive.tasks,supported:__msLive.supported}));
   const state=()=>page.evaluate(()=>({m:NV.s.m,p:NV.s.p,fr:NV.s.fr,file:NV.entry.item.f}));
   const click=loc=>name==='touch'?loc.tap():loc.click();
   const timed=async(label,action,check)=>{
    const start=await page.evaluate(()=>performance.now()),wall=Date.now();
    await action();await ready();const after=await state();assert(check(after),label+' selection mismatch');
    report.interactions.push({label,wallMs:Date.now()-wall,start,end:await page.evaluate(()=>performance.now())});
    return after;
   };
   await cdp.send('Profiler.start');
   const initial=await state();
   assert(await page.locator('#nvFr option').count()>1,'requires at least two frames');
   for(let i=0;i<6;i++){
    const n=await timed('next',()=>click(page.locator('#nvNext')),s=>s.fr!==initial.fr);
    await timed('prev',()=>click(page.locator('#nvPrev')),s=>s.fr===initial.fr&&s.file===initial.file&&s.fr!==n.fr);
   }
   const target=await page.evaluate(()=>[...document.querySelectorAll('#nvBar button[data-m]')].find(b=>!b.disabled&&b.dataset.m!==NV.s.m&&b.getClientRects().length)?.dataset.m);
   assert(target,'no alternative model');
   await timed('model',async()=>{await click(page.locator('#nvBar button[data-m="'+target+'"]:visible').first());await page.waitForFunction(m=>NV.s.m===m,target);},s=>s.m===target);
   const section=page.locator('button[data-r5section="parameters"]:visible').first();
   if(await section.getAttribute('aria-expanded')!=='true')await click(section);
   const picker=page.locator('#msR5ParamPicker');await picker.waitFor({state:'visible'});
   const find=()=>page.evaluate(()=>[...document.querySelectorAll('#msR5ParamPicker button[data-r5param]')].find(b=>!b.disabled&&b.dataset.r5param!==NV.s.p&&b.getClientRects().length)?.dataset.r5param);
   let param=await find();if(!param){await click(picker.locator('button[data-r5group][aria-expanded="false"]:visible').first());param=await find();}
   assert(param,'no alternate parameter');
   await timed('parameter',async()=>{await click(picker.locator('button[data-r5param="'+param+'"]:visible').first());await page.waitForFunction(p=>NV.s.p===p,param);},s=>s.p===param);
   report.hot=summarize((await cdp.send('Profiler.stop')).profile);
   await page.waitForTimeout(1000);
   report.metrics=await page.evaluate(()=>({tasks:__msLive.tasks,events:__msLive.events,heap:performance.memory?.usedJSHeapSize??null,cache:typeof NV_IMAGE_CACHE!=='undefined'?NV_IMAGE_CACHE.stats():null}));
   report.status='pass';
  }catch(e){report.status='fail';report.error=String(e.message).split('\n')[0].slice(0,160);}
  finally{await ctx.close();}
 }
 }finally{await browser.close();fs.writeFileSync('metstat-live-interaction.json',JSON.stringify({at:new Date().toISOString(),note:'Live first-party synthetic observations, no field INP or whole-browser memory claim. Six next/prev round trips; no fullscreen or route stress in this gate.',reports},null,2));}
 if(reports.some(r=>r.status!=='pass'||r.errors||r.version!==reports[0].version))process.exitCode=1;
})().catch(e=>{console.error(e.name);process.exitCode=1;});

const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const root='v85-candidate/assets';
const s=fs.readFileSync(root+'/'+fs.readdirSync(root).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
const a=s.indexOf('const NV_BAR_BOUND='),z=s.indexOf('function nvRegTopSync()',a);assert(a>=0&&z>a);
(async()=>{
 const browser=await chromium.launch();
 try{
  const page=await browser.newPage();
  await page.setContent('<div id="nvBar"></div><select id="nvM"><option value="a">A</option><option value="b">B</option></select>');
  await page.evaluate(()=>{window.$=id=>document.getElementById(id);window.NV={s:{m:'a'}};window.ON={man:{}};window.calls=0;window.nvFillRun=()=>calls++;window.wxModelChips=()=>'<button data-m="a">A</button><button data-m="b">B</button>';});
  await page.addScriptTag({content:s.slice(a,z)});
  await page.evaluate(()=>{nvBarRefresh();window.original=$('nvBar').lastElementChild;for(let i=0;i<100;i++)nvBarRefresh();});
  assert(await page.evaluate(()=>original===$('nvBar').lastElementChild));
  await page.locator('[data-m=b]').click();assert(await page.evaluate(()=>NV.s.m==='b'&&calls===1&&$('nvM').value==='b'));
  await page.evaluate(()=>{$('nvBar').outerHTML='<div id="nvBar"></div>';nvBarRefresh();nvBarRefresh();});
  await page.locator('[data-m=a]').click();assert(await page.evaluate(()=>NV.s.m==='a'&&calls===2));
  await page.evaluate(()=>{const b=$('nvBar').lastElementChild;b.disabled=true;b.dispatchEvent(new MouseEvent('click',{bubbles:true}));});
  assert(await page.evaluate(()=>calls===2));
  await page.evaluate(()=>nvBarRefresh());assert(await page.evaluate(()=>!$('nvBar').lastElementChild.disabled));
  const baseRoot='v85-baseline/assets';
  const old=fs.readFileSync(baseRoot+'/'+fs.readdirSync(baseRoot).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
  for(const [candidate,source] of [[false,old],[true,s]]){
   const i=source.indexOf('function nvBindStage(st)'),j=source.indexOf('/* ---------- لایه‌های برداری',i);assert(i>=0&&j>i);
   for(const touch of [false,true]){
    const ctx=await browser.newContext({viewport:{width:800,height:600},hasTouch:touch,isMobile:touch});
    try{
     const p=await ctx.newPage();
     await p.setContent('<div id="st" style="position:relative;width:600px;height:400px;background:#ddd;touch-action:none"><canvas width="600" height="400"></canvas><div class="nvChipRow" style="position:absolute;right:0;top:0"><div id="nvBar"><button data-m="b" style="width:100px;height:50px">Model B</button></div></div></div>');
     await p.evaluate(()=>{window.NV={view:null};window.NVF={on:false};window.zoom=0;window.chips=0;window.captures=0;window.nvZoom=()=>zoom++;const st=document.getElementById('st');const orig=st.setPointerCapture.bind(st);st.setPointerCapture=id=>{captures++;orig(id);};document.querySelector('#nvBar button').onclick=()=>chips++;});
     await p.addScriptTag({content:source.slice(i,j)});await p.evaluate(()=>nvBindStage(document.getElementById('st')));
     const btn=p.locator('button');if(touch)await btn.tap();else await btn.click();
     const result=await p.evaluate(()=>({chips,captures,zoom}));
     if(candidate){
      assert.equal(result.chips,1);assert.equal(result.captures,0);
      if(!touch){await btn.dblclick();assert.equal(await p.evaluate(()=>zoom),0);}
      await p.mouse.move(150,150);await p.mouse.down();await p.mouse.move(175,165);await p.mouse.up();
      assert(await p.evaluate(()=>captures===1&&!document.getElementById('st').classList.contains('drag')));
      await p.mouse.dblclick(150,150);assert.equal(await p.evaluate(()=>zoom),1);
     }else{assert.equal(result.captures,1);if(!touch)assert.equal(result.chips,0);}
     console.log({candidate,touch,result});
    }finally{await ctx.close();}
   }
  }
  console.log('PASS: stable DOM, real clicks, replacement bar rebinding, no duplicate handlers, disabled guard, external mutation repair');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

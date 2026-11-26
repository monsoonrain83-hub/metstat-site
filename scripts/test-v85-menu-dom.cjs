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
  console.log('PASS: stable DOM, real clicks, replacement bar rebinding, no duplicate handlers, disabled guard, external mutation repair');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

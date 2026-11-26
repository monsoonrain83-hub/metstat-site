// Isolated actual DOM checks; no network or host dependency.
const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const source=fs.readFileSync('web/forecast/parameter-picker.mjs','utf8').replace('export function','function');
(async()=>{
 const browser=await chromium.launch();
 try{
  const page=await browser.newPage();
  await page.setContent('<div id="picker"></div>');
  await page.addScriptTag({content:source+'\nwindow.renderPicker=createParameterPicker();'});
  const results=await page.evaluate(()=>{
   const host=document.querySelector('#picker'),state={parameters:[{id:'t2m',cat:'temp',fa:'دما',en:'Temperature',o:1},{id:'tmax',cat:'temp',fa:'بیشینه',en:'Maximum',o:2},{id:'rain24',cat:'sc',fa:'بارش',en:'Rain'},{id:'x',cat:'other',fa:'<img src=x onerror=alert(1)>'}],categories:[{id:'temp',fa:'دما',en:'Temperature'}],secondary:false,selected:'t2m',group:null,secondaryGroups:[['بارش',['rain']]],text:(f,e)=>f,translate:x=>x};
   state.group=renderPicker(host,state);
   const button=host.querySelector('[data-r5param=t2m]');button.focus();
   let updates=0;const observer=new MutationObserver(rs=>updates+=rs.length);observer.observe(host,{childList:true,subtree:true});
   for(let i=0;i<100;i++)renderPicker(host,state);
   updates+=observer.takeRecords().length;observer.disconnect();
   const stable=button===host.querySelector('[data-r5param=t2m]')&&document.activeElement===button;
   state.selected='tmax';renderPicker(host,state);
   const selected=host.querySelector('[data-r5param=tmax]').getAttribute('aria-pressed')==='true';
   state.group='others';renderPicker(host,state);const literal=host.querySelector('[data-r5param=x]').textContent.includes('<img')&&!host.querySelector('img');
   state.secondary=true;state.group=null;state.selected='rain24';state.group=renderPicker(host,state);
   const secondary=!!host.querySelector('[data-r5param=rain24]');
   state.text=(f,e)=>e;renderPicker(host,state);const language=host.querySelector('[data-r5param=rain24]').textContent==='Rain';
   host.replaceChildren();renderPicker(host,state);const repaired=!!host.querySelector('[data-r5param=rain24]');
   state.parameters=[];renderPicker(host,state);const empty=!!host.querySelector('.hint')&&host.querySelector('[data-r5kind=s]').disabled;
   return {updates,stable,selected,literal,secondary,language,repaired,empty};
  });
  assert.equal(results.updates,0);for(const k of ['stable','selected','literal','secondary','language','repaired','empty'])assert(results[k],k);
  console.log(results);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

// Compare actual extracted V86/V87 render code with current public manifest.
const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const m=JSON.parse(fs.readFileSync('v87-manifest.json','utf8'));
const read=d=>fs.readFileSync(d+'/assets/'+fs.readdirSync(d+'/assets').find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
function source(s){
 const a=s.indexOf('const NV_SEC_GROUPS='),b=s.indexOf(';',a)+1;
 const x=s.includes('function createParameterPicker(')?s.indexOf('/** One owner for R5 parameter picker DOM.'):s.indexOf('function nvrParamRender(){');
 const y=s.indexOf('/* r9.6 P8:',x);
 assert(a>=0&&b>a&&x>=0&&y>x);return s.slice(a,b)+'\n'+s.slice(x,y);
}
const alts=new Set(m.params.map(p=>p.alt).filter(Boolean)),scenarios=[];
for(const lang of ['fa','en'])for(const model of Object.keys(m.models))for(const previous of [false,true]){
 const ids=new Set((previous?m.items_prev:m.items).filter(i=>i.m===model&&i.r==='me'&&!i.p.endsWith('L')).map(i=>i.p));
 const ps=m.params.filter(p=>ids.has(p.id)&&!alts.has(p.id));
 for(const secondary of [false,true])for(const group of [null,'','invalid'])scenarios.push({lang,m:model,ps,secondary,selected:ps.find(p=>(p.cat==='sc')===secondary)?.id||'',group,previous});
}
const fixture='<div class="nvCard" data-rows><select id="mirror" data-mir="nvM"></select></div><div id="onAside"><div class="msR5-periods"></div><div id="msR5ModelRows"></div><div id="msR5ParamPicker"></div></div>'+['nvTc','nvM','nvCat','nvRun','nvX1','nvX2','nvX3','nvX4','nvX5','nvX6'].map(id=>'<select id="'+id+'"></select>').join('')+'<div id="nvR5t"></div>';
(async()=>{
 const browser=await chromium.launch();try{
  const pages=[];
  for(const dir of ['v87-baseline','v87-candidate']){
   const p=await browser.newPage();pages.push(p);await p.setContent(fixture);await p.addScriptTag({content:source(read(dir))});
   await p.evaluate(({cats,models})=>{
    window.$=id=>document.getElementById(id);window.ON={man:{cats,generated:'test'}};window.NV={s:{}};window.NVR={grp:null};window.nvParamsOf=()=>current.ps;window.msR5T=(fa,en)=>LANG==='en'?en:fa;window.tr=x=>x;window.FA=x=>String(x);window.onFmtValid=x=>x;window.onFmtRun=x=>x;window.nvRunSel=()=>current.previous?'2026112518':'2026112600';window.nvMState=k=>k===NV.s.m?'ms-g':'ms-b';
    const opts=(id,options,value)=>{const el=$(id);el.replaceChildren(...options.map(([v,t,d])=>{const o=document.createElement('option');o.value=v;o.textContent=t;o.disabled=!!d;return o;}));el.value=value;};
    opts('nvTc',[['daily','روزانه'],['weekly','هفتگی'],['monthly','ماهانه']],'daily');opts('nvM',models,models[0][0]);opts('nvCat',[['x','دما'],['sc','ثانویه']],'x');for(let i=1;i<=6;i++)opts('nvX'+i,[['m','direct'],['s','derived'],['x','temperature'],['sc','secondary']],'m');opts('nvRun',[['2026112600','Current'],['2026112518','Previous']],'2026112600');
    window.apply=z=>{window.current=z;window.LANG=z.lang;NV.s={m:z.m,p:z.selected,cat:z.secondary?'sc':'x',fr:'1'};NV.entry={item:{v:'1',s:6}};NVR.grp=z.group;$('nvM').value=z.m;$('nvCat').value=NV.s.cat;nvrSync(true);};
    window.snapshot=()=>({picker:$('msR5ParamPicker').innerHTML,period:document.querySelector('.msR5-periods').innerHTML,model:$('msR5ModelRows').innerHTML,checked:[...$('msR5ModelRows').querySelectorAll('input')].map(x=>x.checked),mirror:[...$('mirror').options].map(o=>[o.value,o.textContent,o.disabled]),mirrorValue:$('mirror').value,category:[...$('nvX5').options].map(o=>[o.value,o.textContent,o.disabled]),categoryValue:$('nvX5').value,group:NVR.grp});
   },{cats:m.cats,models:Object.keys(m.models).map(k=>[k,k+' — مدل (اروپا)',false])});
  }
  for(let i=0;i<scenarios.length;i+=40){
   const batch=scenarios.slice(i,i+40);
   const a=await pages[0].evaluate(zs=>zs.map(z=>{apply(z);return snapshot();}),batch);
   const b=await pages[1].evaluate(zs=>zs.map(z=>{apply(z);return snapshot();}),batch);
   assert.deepEqual(b,a,'sidebar output mismatch batch '+i);
  }
  const report={scenarios:scenarios.length,manifestRows:m.items.length+m.items_prev.length,results:[]};
  for(const p of pages){
   report.results.push(await p.evaluate(()=>{
    const ids=['msR5ParamPicker','msR5ModelRows','mirror','nvX5'],nodes=ids.map(id=>$(id).firstElementChild),period=document.querySelector('.msR5-periods').firstElementChild,target=$('msR5ParamPicker').querySelector('button');target.focus();
    const o=new MutationObserver(()=>{});for(const id of ids)o.observe($(id),{childList:true,subtree:true});o.observe(period.parentElement,{childList:true,subtree:true});
    for(let i=0;i<100;i++){NV.s.fr=String(i);NV.entry.item.v=String(i);nvrSync(true);}
    const mutations=o.takeRecords().length;o.disconnect();
    return {mutations,stable:ids.every((id,i)=>$(id).firstElementChild===nodes[i])&&period===document.querySelector('.msR5-periods').firstElementChild,focus:document.activeElement===target};
   }));
  }
  assert(report.results[0].mutations>0);assert.deepEqual(report.results[1],{mutations:0,stable:true,focus:true});
  // Confirm external changes to checked state are repaired, and text is not parsed as HTML.
  const safe=await pages[1].evaluate(()=>{
    const el=document.createElement('select');document.body.append(el);
    NVR_CONTROLS.options(el,[{value:'x',label:'<img src=x onerror=alert(1)>',disabled:false}],'x');
    const literal=el.options[0].textContent==='<img src=x onerror=alert(1)>'&&!el.querySelector('img');
    const host=$('msR5ModelRows'),selected=$('nvM').value;
    host.querySelector('input:checked').checked=false;nvrSync(true);
    return literal&&host.querySelector('input:checked')?.value===selected;
  });assert(safe);
  fs.writeFileSync('v87-sidebar-report.json',JSON.stringify(report,null,2));console.log(report);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

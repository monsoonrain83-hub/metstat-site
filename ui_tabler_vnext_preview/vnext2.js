/* MetStat vNext2 interaction layer. Standalone demo only; not a production adapter.
 * No remote calls, eval/innerHTML, external code, timers used for network.
 * Emits existing 'metstat:ui-action' events without altering forecast algorithms.
 */
(() => {
'use strict';
const root=document.getElementById('msApp');
if(!root)return;
const $=id=>document.getElementById(id);
const legacy=window.MetStatLegacyPalettes;
if(!legacy || !legacy.groups || !legacy.palettes)return;
let paletteId='wu_precip24';
let lastGroup='precip';
let soundEnabled=true;
let audioCtx;
let playing=false;
let playTimer=null;
function emit(type,payload){document.dispatchEvent(new CustomEvent('metstat:ui-action',{detail:{type,...payload}}));}
function playSound(selected){
 if(!soundEnabled)return;
 try{
   const Ctx=window.AudioContext||window.webkitAudioContext;
   if(!Ctx)return;
   audioCtx=audioCtx||new Ctx();
   if(audioCtx.state==='suspended')audioCtx.resume().catch(()=>{});
   const now=audioCtx.currentTime;
   const osc=audioCtx.createOscillator(),g=audioCtx.createGain();
   osc.type='sine';
   osc.frequency.setValueAtTime(selected?560:470,now);
   osc.frequency.exponentialRampToValueAtTime(selected?295:230,now+.072);
   g.gain.setValueAtTime(.0001,now);
   g.gain.exponentialRampToValueAtTime(.026,now+.008);
   g.gain.exponentialRampToValueAtTime(.0001,now+.09);
   osc.connect(g);g.connect(audioCtx.destination);osc.start(now);osc.stop(now+.10);
   osc.onended=()=>{osc.disconnect();g.disconnect();};
 }catch(e){ /* Audio is noncritical; all UI actions still work. */ }
}
function soundToggle(){
 soundEnabled=!soundEnabled;
 const btn=$('msSoundToggle');btn.setAttribute('aria-pressed',String(soundEnabled));
 btn.setAttribute('aria-label',soundEnabled?'بی‌صدا کردن صدای کلیک':'فعال‌کردن صدای کلیک');
 btn.title=soundEnabled?'صدای ظریف کلیک: روشن':'صدای کلیک: خاموش';
}
function closeMenus(except){
 root.querySelectorAll('[data-menu-trigger]').forEach(btn=>{
  if(btn===except)return;
  btn.setAttribute('aria-expanded','false');
  const panel=$(btn.getAttribute('aria-controls'));if(panel)panel.hidden=true;
 });
}
function toggleMenu(btn){
 const panel=$(btn.getAttribute('aria-controls'));
 if(!panel)return;
 const shouldOpen=btn.getAttribute('aria-expanded')!=='true';
 closeMenus(btn);btn.setAttribute('aria-expanded',String(shouldOpen));panel.hidden=!shouldOpen;
 if(shouldOpen)root.querySelectorAll('.ms-top-item').forEach(x=>x.dataset.selected=String(x===btn));
 else syncNav();
}
const routeToGroup=path=>{
 if(path.includes('weather-models')||path.includes('forecast-verification')||path.includes('flash-flood'))return 'weather-models';
 if(path.includes('meteorological-tools')||path.includes('rainfall-isohyet'))return 'meteorological-tools';
 if(path.includes('synoptic-analysis'))return 'synoptic-analysis';
 return 'climate-analytics';
};
function syncNav(){
 const activeRoute=window.MetStatShellPreview?.getRoute?.()||location.pathname;
 const group=routeToGroup(activeRoute);
 root.querySelectorAll('.ms-top-item').forEach(btn=>btn.dataset.selected=String(btn.closest('.ms-nav-group')?.dataset.navGroup===group));
 root.querySelectorAll('.ms-nav-menu a[data-route]').forEach(a=>{
  if(a.pathname===activeRoute)a.setAttribute('aria-current','page');
  else a.removeAttribute('aria-current');
 });
}
function closePickers(except){
 root.querySelectorAll('[data-param-open]').forEach(btn=>{
  if(btn===except)return;
  btn.setAttribute('aria-expanded','false');
  const pop=$(btn.getAttribute('aria-controls'));if(pop)pop.hidden=true;
 });
}
function togglePicker(btn){
 const panel=$(btn.getAttribute('aria-controls'));if(!panel)return;
 const show=btn.getAttribute('aria-expanded')!=='true';
 closePickers(btn);btn.setAttribute('aria-expanded',String(show));panel.hidden=!show;
}
function chooseParameter(btn){
 const type=btn.dataset.paramChoice,sel=$(type==='main'?'msMainParameter':'msSecondaryParameter');
 const option=Array.from(sel.options).find(o=>o.value===btn.dataset.paramValue);
 if(!option)return;
 sel.value=option.value;
 $(type==='main'?'msParamValueMain':'msParamValueSecondary').textContent=option.textContent;
 const trigger=root.querySelector('[data-param-open="'+type+'"]');
 closePickers();
 root.querySelectorAll('[data-param-choice="'+type+'"]').forEach(x=>x.setAttribute('aria-pressed',String(x===btn)));
 sel.dispatchEvent(new Event('change',{bubbles:true}));
 if(type==='main')renderPaletteList();
 emit('parameter-selection',{type,value:option.value});
 if(trigger)trigger.focus();
}
const groupForParam=id=>{
 if(['p24','p6','p1','pacc'].includes(id))return 'precip';
 if(['t2m','t850'].includes(id))return 'temp';
 if(id==='tanom')return 'tanom';
 if(id==='rh')return 'rh';
 if(id==='cape')return 'cape';
 if(id==='wind')return 'wind';
 return null; // do not INVENT scientific palettes for unrelated parameters
};
const colorsFor=(id,group)=>{
 if(id==='windy')return legacy.windy[group==='precip'||group==='snow'?'precip':'temp'];
 const colors=legacy.palettes[id];
 return Array.isArray(colors)?colors:null;
};
function gradientFrom(colors){
 if(!colors||colors.length<2)return 'repeating-linear-gradient(90deg,#d5e4ec 0 10px,#b8d0de 10px 20px)';
 const unit=100/colors.length;
 const arr=[];
 for(let i=0;i<colors.length;i++){
  const c=colors[i];if(!/^#[a-fA-F0-9]{6}$/.test(c))return 'linear-gradient(to right,#ddd,#aaa)';
  arr.push(`${c} ${(unit*i).toFixed(3)}%`,`${c} ${(unit*(i+1)).toFixed(3)}%`);
 }
 return 'linear-gradient(to right,'+arr.join(',')+')';
}
function numericLabels(id,colors){
 const target=$('msPaletteNumericLabels');target.replaceChildren();
 const e=legacy.edges[id];
 if(!e||!Array.isArray(e)||!colors||e.length!==colors.length){
  const span=document.createElement('span');span.textContent='اعداد معتبر پس از اتصال مقیاس پارامتر';span.style.cssText='left:50%;transform:translateX(-50%);width:max-content;max-width:95%';
  target.appendChild(span);return;
 }
 const positions=[0,.2,.4,.6,.8,1];
 for(let i=0;i<positions.length;i++){
  const p=positions[i],idx=Math.round(p*(e.length-1));
  const v=e[idx],node=document.createElement('span');
  node.style.left=(p*100)+'%';
  node.textContent=Number.isFinite(v)?new Intl.NumberFormat('fa-IR',{maximumFractionDigits:2}).format(v):String(v);
  target.appendChild(node);
 }
}
function selectPalette(id){
 const group=groupForParam($('msMainParameter').value);
 const entry=(legacy.groups[group]||[]).find(a=>a[1]===id);
 const colors=colorsFor(id,group);
 if(!entry||!colors||colors.length<2)return false;
 paletteId=id;lastGroup=group;
 $('msPaletteTitle').textContent=entry[0];
 $('msSelectedPaletteStrip').style.background=gradientFrom(colors);
 numericLabels(id,colors);
 root.querySelectorAll('[data-palette-id]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.paletteId===id)));
 $('msPaletteOptions').hidden=true;$('msPaletteTrigger').setAttribute('aria-expanded','false');
 emit('palette-selection',{parameter:$('msMainParameter').value,group,paletteId:id});
 return true;
}
function renderPaletteList(){
 const group=groupForParam($('msMainParameter').value);
 const list=$('msPaletteList');list.replaceChildren();
 if(!group){
  paletteId=null;
  const info=document.createElement('p');info.className='ms-palette-notice';info.textContent='برای این پارامتر در کتابخانه قبلی، کالربار مستند موجود نیست. بعد از اتصال فایل رنگ و مرزهای واقعی فعال می‌شود.';list.appendChild(info);
  $('msPaletteTitle').textContent='رنگ‌بندی اصلی پارامتر (منتظر مقیاس معتبر)';
  $('msSelectedPaletteStrip').style.background=gradientFrom(null);
  numericLabels('__missing__',null);lastGroup='';return;
 }
 const options=legacy.groups[group]||[];
 for(const [name,id] of options){
  const colors=colorsFor(id,group);
  const btn=document.createElement('button');btn.type='button';btn.className='ms-palette-option';btn.dataset.paletteId=id;
  btn.disabled=!colors||colors.length<2;
  const title=document.createElement('span');title.className='ms-palette-name';title.textContent=name;
  const bar=document.createElement('span');bar.className='ms-palette-swatch';bar.setAttribute('aria-hidden','true');bar.style.background=gradientFrom(colors);
  const type=document.createElement('span');type.className='ms-palette-unit';type.textContent=btn.disabled?'فایل رنگ لازم است':legacy.edges[id]&&legacy.edges[id].length===colors.length?'با مقیاس':'بدون مقیاس';
  btn.setAttribute('aria-label',name+(btn.disabled?' (فاقد رنگ‌های تأییدشده)':''));
  btn.setAttribute('aria-pressed',String(id===paletteId));
  btn.append(title,bar,type);list.appendChild(btn);
 }
 const selected=options.some(([_,id])=>id===paletteId && colorsFor(id,group));
 if(!selected){const first=options.find(([_,id])=>colorsFor(id,group));if(first)selectPalette(first[1]);}
 else selectPalette(paletteId);
}
function paletteToggle(){
 const p=$('msPaletteOptions'),btn=$('msPaletteTrigger');const open=p.hidden;
 p.hidden=!open;btn.setAttribute('aria-expanded',String(open));
 if(open)p.querySelector('button:not(:disabled)')?.focus();
}
function getHours(){return Array.from($('msLead').options).map(x=>Number(x.value)).filter(Number.isFinite).sort((a,b)=>a-b)}
function currentLead(){return Number($('msLead').value)}
function stepLead(dir){
 const hours=getHours(),now=currentLead();const size=Number($('msStepSize').value)||24;
 const target=Math.max(hours[0],Math.min(hours[hours.length-1],now+dir*size));
 const closest=hours.reduce((a,b)=>Math.abs(b-target)<Math.abs(a-target)?b:a,hours[0]);
 $('msLeadRange').value=String(closest);
 $('msLeadRange').dispatchEvent(new Event('input',{bubbles:true}));
}
function stopPlayback(){playing=false;clearTimeout(playTimer);playTimer=null;const btn=$('msTimelinePlay');btn.setAttribute('aria-pressed','false');btn.setAttribute('aria-label','پخش گام‌های پیش‌بینی');btn.textContent='▶'}
function playTick(){if(!playing)return;const before=currentLead();stepLead(1);if(currentLead()===before){stopPlayback();return;}playTimer=setTimeout(playTick,800)}
function startPlayback(){if(playing){stopPlayback();return}playing=true;const btn=$('msTimelinePlay');btn.setAttribute('aria-pressed','true');btn.setAttribute('aria-label','توقف پخش گام‌های پیش‌بینی');btn.textContent='❚❚';playTimer=setTimeout(playTick,800)}
function updateThemeContext(){
 // The site homepage atmospheric treatment is decorative only; never embedded into forecast rasters.
 document.body.dataset.homeSurface='true';
}
root.addEventListener('click',e=>{
 const btn=e.target.closest('button');
 if(btn && !btn.disabled && !btn.classList.contains('ms-rail-chip'))playSound(btn.getAttribute('aria-pressed')==='false'||btn.getAttribute('aria-expanded')==='false');
 const navTrigger=e.target.closest('[data-menu-trigger]');if(navTrigger){toggleMenu(navTrigger);return}
 if(e.target.closest('.ms-nav-menu a[data-route]')){closeMenus();syncNav();return}
 if(e.target.closest('a[data-route]')){closeMenus();syncNav();return}
 if(e.target.closest('[data-period]')){syncNav();stopPlayback();return}
 const picker=e.target.closest('[data-param-open]');if(picker){togglePicker(picker);return}
 const choice=e.target.closest('[data-param-choice]');if(choice){chooseParameter(choice);return}
 const selectedPalette=e.target.closest('[data-palette-id]');if(selectedPalette){selectPalette(selectedPalette.dataset.paletteId);$('msPaletteTrigger').focus();return}
 if(e.target.closest('[data-palette-toggle]')){paletteToggle();return}
 if(e.target.closest('#msSoundToggle')){soundToggle();return}
 const timeline=e.target.closest('[data-timeline]');if(timeline){
  if(timeline.dataset.timeline==='play')startPlayback();
  else {stopPlayback();stepLead(timeline.dataset.timeline==='next'?1:-1)}
  return;
 }
 if(e.target.closest('[data-action="reset"]')){
  stopPlayback();$('msParamValueMain').textContent=$('msMainParameter').selectedOptions[0].textContent;
  $('msParamValueSecondary').textContent=$('msSecondaryParameter').selectedOptions[0].textContent;
  renderPaletteList();syncNav();return;
 }
});
root.addEventListener('change',e=>{
 if(e.target.id==='msMainParameter')renderPaletteList();
});
document.addEventListener('click',e=>{
 if(!e.target.closest('.ms-nav')){closeMenus();syncNav();}
 if(!e.target.closest('.ms-parameter-field'))closePickers();
 if(!e.target.closest('.ms-colorbar-picker')){$('msPaletteOptions').hidden=true;$('msPaletteTrigger').setAttribute('aria-expanded','false');}
});
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){
  closeMenus();closePickers();$('msPaletteOptions').hidden=true;$('msPaletteTrigger').setAttribute('aria-expanded','false');stopPlayback();
 }
});
window.addEventListener('popstate',()=>{syncNav();stopPlayback()});
window.addEventListener('pagehide',stopPlayback);
// Bootstrap: preserve real model-status chip colors — never touch them here.
updateThemeContext();syncNav();renderPaletteList();
root.querySelectorAll('[data-param-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.paramValue===(b.dataset.paramChoice==='main'?$('msMainParameter').value:$('msSecondaryParameter').value))));
window.MetStatUIVnext2=Object.freeze({getPalette:()=>paletteId,isSoundEnabled:()=>soundEnabled,stopPlayback});
})();
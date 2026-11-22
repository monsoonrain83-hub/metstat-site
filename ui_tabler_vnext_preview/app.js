/* MetStat UI Shell vNext, deliberately isolated from the production NWP runtime.
 * All controls are real DOM elements, not clones of legacy controls.
 * An optional adapter can listen for 'metstat:ui-action' and 'metstat:state-change'
 * and update the existing Map engine; demo mode never asserts a live forecast.
 */
(() => {
'use strict';
const root = document.getElementById('msApp');
if (!root) return;
const $ = id => document.getElementById(id);
const status = $('msActionStatus');
const toast = $('msToast');
const model = $('msModel'), mainParam = $('msMainParameter'), lead = $('msLead'), run = $('msRun');
const layerPanel = $('msLayerPanel');
const mapColumn = root.querySelector('.ms-map-column');
const routes = Object.freeze({
  '/monitoring-forecast/weather-models': ['weather-models', 'مدل‌های هواشناسی', 'انتخاب مدل، بازه پیش‌بینی و پارامتر — در یک محیط ثابت و یکپارچه'],
  '/monitoring-forecast/weather-models/daily': ['weather-models', 'پیش‌بینی روزانه', 'مدل‌های عددی و فریم‌های معتبر روزانه'],
  '/monitoring-forecast/weather-models/weekly': ['weather-models', 'پیش‌بینی هفتگی', 'مدل‌های هفتگی و آنومالی‌ها'],
  '/monitoring-forecast/weather-models/monthly': ['weather-models', 'پیش‌بینی ماهانه', 'مدل‌ها و بازه‌های ماهانه'],
  '/monitoring-forecast/weather-models/seasonal': ['weather-models', 'پیش‌بینی فصلی', 'چشم‌انداز سه‌ماهه و آنومالی‌ها'],
  '/monitoring-forecast/weather-models/ensemble': ['weather-models', 'پیش‌بینی انسمبل', 'اعضای انسمبل و محصولات احتمالاتی'],
  '/meteorological-tools': ['meteorological-tools','جعبه ابزار هواشناسی','محصولات و ابزارهای پردازشی'],
  '/synoptic-analysis': ['synoptic-analysis','تحلیل نقشه‌های همدیدی','تحلیل ترازهای مختلف و وضعیت جو'],
  '/climate-analytics': ['climate-analytics','تحلیل‌های اقلیمی','شاخص‌ها، سری‌های زمانی و داده‌های اقلیمی'],
  '/rainfall-isohyet': ['rainfall-isohyet','تهیه نقشه همبارش','بانک ایستگاه‌ها و پردازش گزارش‌های بارندگی'],
  '/forecast-verification': ['forecast-verification','پایش دقت مدل‌ها','ارزیابی و صحت‌سنجی مدل‌های هواشناسی'],
  '/flash-flood': ['flash-flood','پایش سیلاب ناگهانی','ارزیابی ریسک بر پایه بارش، DEM و حوضه‌های آبریز']
});
let routePath = '/monitoring-forecast/weather-models';
let simulatedZoom = 100;
let toastTimeout;
let layerOpen = false;
function speak(message){
  status.textContent=message;
  toast.textContent=message;
  toast.dataset.visible='true';
  window.clearTimeout(toastTimeout);
  toastTimeout=window.setTimeout(()=>{toast.dataset.visible='false'},2600);
}
function emit(type,payload={}){
  document.dispatchEvent(new CustomEvent('metstat:ui-action',{detail:{type,...payload},bubbles:false}));
}
function safePath(url){
  try {const u=new URL(url,location.origin); return u.origin===location.origin && Object.prototype.hasOwnProperty.call(routes,u.pathname.replace(/\/+$/,'')||'/')?u.pathname.replace(/\/+$/,''):null} catch {return null}
}
function currentPath(){return safePath(location.href) || '/monitoring-forecast/weather-models'}
function renderRoute(path,updateHistory=true){
  const dest=safePath(path);if(!dest){speak('مسیر در فهرست مجاز این پیش‌نمایش نیست');return false}
  routePath=dest;
  const [nav,title,desc]=routes[dest];
  $('msPageTitle').textContent=title;
  $('msPageSubtitle').textContent=desc;
  $('msRouteLabel').textContent=dest;
  document.title='MetStat — '+title+' | پیش‌نمایش';
  root.querySelectorAll('[data-route]').forEach(a=>{
    const selected=a.dataset.nav===nav;
    if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  });
  const tab=dest.split('/').pop();
  const period=root.querySelector('[data-period="'+tab+'"]');
  if(period)syncPeriod(tab,false);
  if(updateHistory && location.pathname!==dest)history.pushState({msRoute:dest},'',dest);
  return true;
}
function syncPeriod(period,pushRoute=true){
  root.querySelectorAll('[data-period]').forEach(b=>{
    const selected=b.dataset.period===period;
    b.classList.toggle('active',selected);
    b.setAttribute('aria-pressed',String(selected));
  });
  if(pushRoute)renderRoute('/monitoring-forecast/weather-models/'+period);
  emit('forecast-period',{period});
}
function syncModel(value){
  if(!Array.from(model.options).some(o=>o.value===value)) return;
  model.value=value;
  root.querySelectorAll('[data-quick-model]').forEach(btn=>{
    const active=btn.dataset.quickModel===value;
    btn.classList.toggle('is-selected',active);
    btn.setAttribute('aria-pressed',String(active));
  });
  $('msStatSource').textContent=model.selectedOptions[0].textContent.replace(' — یکپارچه','');
  updateCaption();emit('model',{model:value});
}
function updateCaption(){
  $('msMapTitle').textContent=mainParam.selectedOptions[0].textContent+' · '+model.value.toUpperCase();
  $('msMapValid').textContent='ران '+run.value+'Z | +'+lead.value+' ساعت';
  $('msStatValid').textContent='+'+lead.value+' ساعت';
  $('msLeadText').textContent='+'+lead.value+' ساعت';
}
function syncLead(value){
  const v=Number(value);if(!Number.isFinite(v))return;
  const options=Array.from(lead.options).map(o=>Number(o.value));
  const best=options.reduce((acc,n)=>Math.abs(n-v)<Math.abs(acc-v)?n:acc,options[0]);
  lead.value=String(best);$('msLeadRange').value=String(best);
  updateCaption();emit('forecast-lead',{leadHours:best});
}
function setLayerPanel(open,focus=false){
  layerOpen=!!open;
  layerPanel.dataset.open=String(layerOpen);
  layerPanel.setAttribute('aria-hidden',String(!layerOpen));
  layerPanel.inert=!layerOpen;
  root.querySelectorAll('[data-action="layers"], [data-action="wind"], [data-action="settings"]').forEach(b=>{
    b.dataset.open=String(layerOpen);
    b.setAttribute('aria-expanded',String(layerOpen));
  });
  if(layerOpen && focus)layerPanel.querySelector('[data-action="close-layers"]').focus();
  if(!layerOpen && focus)root.querySelector('[data-action="layers"]').focus();
}
function setDesktopFullscreen(active){
  mapColumn.classList.toggle('ms-local-fullscreen',active);
  root.querySelector('[data-action="fullscreen"]').setAttribute('aria-pressed',String(active));
  emit('fullscreen',{enabled:active});
}
function updateLayerCounter(){
  const n=root.querySelectorAll('[data-layer]:checked').length;
  $('msStatLayers').textContent=n+' لایه';
}
function layerChange(target){
  const key=target.dataset.layer;
  const enabled=target.checked;
  emit('layer-toggle',{layer:key,enabled});
  updateLayerCounter();
  speak('لایه «'+target.closest('label').querySelector('span').textContent+'» '+(enabled?'فعال':'غیرفعال')+' شد (نمایشی)');
}
root.addEventListener('change',e=>{
  const t=e.target;
  if(t===model){syncModel(model.value);return}
  if(t===mainParam||t===$('msSecondaryParameter')||t===run){
    updateCaption();emit('forecast-setting',{model:model.value,parameter:mainParam.value,secondary:$('msSecondaryParameter').value,run:run.value});return;
  }
  if(t===lead){syncLead(t.value);return}
  if(t.matches('[data-layer]')){layerChange(t);return}
  if(t.matches('.ms-geo-select select')){
    emit('geo-selection',{tier:t.id,value:t.value});
    speak('محدوده انتخاب شد؛ زوم واقعی نیازمند مرز جغرافیایی معتبر است');
  }
});
root.addEventListener('input',e=>{
  const t=e.target;
  if(t.id==='msLeadRange'){syncLead(t.value);return}
  const ranges={'msLineWidth':['msLineWidthOutput',' px','lineWidth'], 'msLabelSize':['msLabelSizeOutput',' px','labelSize'], 'msWindSpeed':['msWindSpeedOutput',' ×','windSpeed']};
  if(ranges[t.id]){const [out,unit,prop]=ranges[t.id];$(out).textContent=t.value+unit;emit('map-display',{property:prop,value:Number(t.value)});}
});
root.addEventListener('click',e=>{
  const anchor=e.target.closest('a[data-route]');
  if(anchor){e.preventDefault();renderRoute(anchor.href);return}
  const period=e.target.closest('[data-period]');if(period){syncPeriod(period.dataset.period);return}
  const chip=e.target.closest('[data-quick-model]');if(chip){syncModel(chip.dataset.quickModel);return}
  const action=e.target.closest('[data-action]');if(!action)return;
  switch(action.dataset.action){
  case 'layers': case 'settings':case 'wind':setLayerPanel(!layerOpen,true);break;
  case 'close-layers':setLayerPanel(false,true);break;
  case 'zoom-in':simulatedZoom=Math.min(200,simulatedZoom+10);$('msZoomInfo').textContent='بزرگ‌نمایی نمایشی: '+simulatedZoom+'٪';emit('zoom',{direction:1});break;
  case 'zoom-out':simulatedZoom=Math.max(50,simulatedZoom-10);$('msZoomInfo').textContent='بزرگ‌نمایی نمایشی: '+simulatedZoom+'٪';emit('zoom',{direction:-1});break;
  case 'extent':simulatedZoom=100;$('msZoomInfo').textContent='بزرگ‌نمایی نمایشی: ۱۰۰٪';emit('full-extent');break;
  case 'refresh':emit('refresh');speak('درخواست تازه‌سازی ثبت شد (بدون درخواست شبکه در حالت نمایشی)');break;
  case 'fullscreen':setDesktopFullscreen(!mapColumn.classList.contains('ms-local-fullscreen'));break;
  case 'apply':emit('forecast-apply',{model:model.value,period:root.querySelector('[data-period].active')?.dataset.period,parameter:mainParam.value,run:run.value,leadHours:Number(lead.value)});speak('انتخاب‌ها آماده ارسال به موتور نقشه‌اند؛ داده واقعی متصل نیست');break;
  case 'reset':mainParam.value='p24';$('msSecondaryParameter').value='none';run.value='12';syncLead(24);syncModel('ecmwf');syncPeriod('daily');speak('تنظیمات به حالت پایه بازگشت');break;
  case 'info':speak('این نسخه فقط برای آزمون چیدمان، دسترس‌پذیری و مسیرهاست');break;
  case 'language':speak('ترجمه انگلیسی در مرحله اتصال به i18n اصلی فعال می‌شود');break;
  }
});
// Disclosure behavior: pointer hover expands visually; click explicitly pins on touch.
root.addEventListener('pointerup',e=>{
  if(e.pointerType!=='touch' && e.pointerType!=='pen')return;
  const b=e.target.closest('.ms-rail-chip,.ms-rail-tool,.ms-overlay-button');
  if(!b)return;
  root.querySelectorAll('.ms-rail-chip,.ms-rail-tool,.ms-overlay-button').forEach(x=>{
    if(x!==b)x.removeAttribute('data-expanded');
  });
  b.dataset.expanded=b.dataset.expanded==='true'?'false':'true';
});
document.addEventListener('pointerdown',e=>{
  if(layerOpen && !layerPanel.contains(e.target) && !e.target.closest('.ms-overlay-group'))setLayerPanel(false);
  if(!e.target.closest('.ms-rail-chip,.ms-rail-tool,.ms-overlay-button'))root.querySelectorAll('[data-expanded]').forEach(x=>x.removeAttribute('data-expanded'));
});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    if(layerOpen){setLayerPanel(false,true);return}
    if(mapColumn.classList.contains('ms-local-fullscreen'))setDesktopFullscreen(false);
  }
});
window.addEventListener('popstate',()=>renderRoute(currentPath(),false));
renderRoute(currentPath(),false);syncModel('ecmwf');syncLead(24);updateLayerCounter();
setLayerPanel(false);
// Testable, read-only interface to the isolated preview state; no production globals overwritten.
window.MetStatShellPreview=Object.freeze({getRoute:()=>routePath,getModel:()=>model.value,isPanelOpen:()=>layerOpen,getLayerPanel:()=>layerPanel});
})();

/* MetStat isohyet UI augmentation for existing Leaflet map instance.
 * Requires a cross-origin-safe basemap and html2canvas 1.4+ for PNG capture.
 * Existing site must supply actual administrative layers and logo path.
 */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatMapTools=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const CSS=`
.metstat-map-toolbar{direction:rtl;display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 12px;background:#f8fafc;border:1px solid #dbe3ec;border-radius:10px;margin:0 0 8px;color:#142a41;font:13px Tahoma,Arial,sans-serif}
.metstat-map-toolbar button{appearance:none;cursor:pointer;border:1px solid #9fb3c8;border-radius:8px;background:#fff;color:#15334f;padding:8px 14px;font-weight:bold}
.metstat-map-toolbar button.metstat-save{background:#0d5a98;color:white;border-color:#0d5a98}
.metstat-map-toolbar label{display:flex;align-items:center;gap:5px;white-space:nowrap;cursor:pointer}
.metstat-map-toolbar input[type=checkbox]{accent-color:#0d5a98}
.metstat-map-count{font-weight:bold;margin-inline-start:auto}
.metstat-map-error{font-size:12px;color:#b42318}
/* No white outline, opaque tooltip background, or text stroke on station labels. */
.metstat-map-label,.metstat-station-label,.leaflet-tooltip.metstat-station-tooltip{color:#111!important;background:transparent!important;border:0!important;box-shadow:none!important;text-shadow:none!important;-webkit-text-stroke:0 transparent!important;font-weight:700;font-size:12px}
.leaflet-tooltip.metstat-station-tooltip::before{display:none}
`;
function element(tag,props={},parent){const e=document.createElement(tag);Object.assign(e,props);if(parent)parent.appendChild(e);return e;}
function assertLayer(layer){return layer&&typeof layer.addTo==='function';}
function injectStyles(){if(document.getElementById('metstat-map-styles'))return;const s=element('style',{id:'metstat-map-styles'},document.head);s.textContent=CSS;}
function textRTL(ctx,text,x,y,maxWidth){ctx.textAlign='right';ctx.direction='rtl';ctx.fillText(text,x,y,maxWidth);}
function loadImage(url){return new Promise((resolve,reject)=>{const img=new Image();img.crossOrigin='anonymous';img.onload=()=>resolve(img);img.onerror=reject;img.src=url;});}
async function exportPng(cfg){
 if(typeof globalThis.html2canvas!=='function')throw new Error('کتابخانه html2canvas برای خروجی PNG بارگذاری نشده است.');
 const map=cfg.map,mapEl=cfg.mapElement;
 if(!map||!mapEl)throw new Error('Map instance is missing');
 if(typeof map.whenReady==='function')await new Promise(resolve=>map.whenReady(resolve));
 const scale=Math.max(2,Math.min(3,Number(cfg.exportScale)||2));
 const mapCanvas=await globalThis.html2canvas(mapEl,{backgroundColor:'#fff',useCORS:true,allowTaint:false,scale,logging:false});
 const width=mapCanvas.width,top=Math.round(110*scale),bottom=Math.round(58*scale);
 const out=document.createElement('canvas');out.width=width;out.height=top+mapCanvas.height+bottom;
 const ctx=out.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,out.width,out.height);
 ctx.fillStyle='#104c80';ctx.fillRect(0,0,width,Math.round(7*scale));
 ctx.fillStyle='#142a41';ctx.font=`bold ${25*scale}px Tahoma,Arial`;textRTL(ctx,cfg.title||'نقشه هم‌بارش ایستگاه‌های هواشناسی',width-24*scale,44*scale,width-165*scale);
 ctx.fillStyle='#455d78';ctx.font=`${14*scale}px Tahoma,Arial`;
 textRTL(ctx,[cfg.reportDate||'',cfg.province||'',cfg.unitLabel||'میلی‌متر'].filter(Boolean).join('  |  '),width-24*scale,76*scale,width-160*scale);
 if(cfg.logoUrl){try{const img=await loadImage(cfg.logoUrl);const maxW=117*scale,maxH=76*scale;const ratio=Math.min(maxW/img.width,maxH/img.height);ctx.drawImage(img,20*scale,17*scale,img.width*ratio,img.height*ratio);}catch(e){ctx.fillStyle='#104c80';ctx.font=`bold ${22*scale}px Arial`;ctx.textAlign='left';ctx.fillText('MetStat',20*scale,57*scale);}}
 else{ctx.fillStyle='#104c80';ctx.font=`bold ${22*scale}px Arial`;ctx.textAlign='left';ctx.fillText('MetStat',20*scale,57*scale);}
 ctx.drawImage(mapCanvas,0,top);
 ctx.strokeStyle='#d5dfeb';ctx.beginPath();ctx.moveTo(0,top+mapCanvas.height);ctx.lineTo(width,top+mapCanvas.height);ctx.stroke();
 ctx.font=`${13*scale}px Tahoma,Arial`;ctx.fillStyle='#3b536d';
 textRTL(ctx,`ایستگاه‌های گزارش: ${cfg.totalCount ?? '—'} | روی نقشه: ${cfg.mappedCount ?? '—'} | در انتظار بررسی: ${cfg.pendingCount ?? '—'}`,width-22*scale,top+mapCanvas.height+29*scale,width-40*scale);
 ctx.textAlign='left';ctx.direction='ltr';ctx.font=`${10*scale}px Arial`;
 ctx.fillText(cfg.attribution||'Map data: OpenStreetMap contributors (where applicable)',17*scale,top+mapCanvas.height+48*scale,width-30*scale);
 let blob;
 try{blob=await new Promise(resolve=>out.toBlob(resolve,'image/png'));}catch(e){throw new Error('Tile CORS prevents image export; use a CORS-enabled tile server.');}
 if(!blob)throw new Error('تصویر قابل تولید نیست؛ محدودیت CORS یا حافظه بررسی شود.');
 const href=URL.createObjectURL(blob),a=document.createElement('a');a.href=href;a.download=cfg.fileName||'MetStat_Isohyet.png';a.click();setTimeout(()=>URL.revokeObjectURL(href),2500);return {width:out.width,height:out.height,bytes:blob.size};
}
/** Existing Leaflet map and existing boundary/center layers are required. */
function install(cfg){
 if(!cfg||!cfg.map||!cfg.mapElement)throw new Error('map, mapElement are required');
 injectStyles();const host=cfg.mapElement.parentNode;const bar=element('div',{className:'metstat-map-toolbar'});host.insertBefore(bar,cfg.mapElement);
 const save=element('button',{type:'button',textContent:'ذخیره PNG',className:'metstat-save'},bar);
 const countLabel=element('span',{className:'metstat-map-count',textContent:''},bar);
 const opts=[['countyBorders','مرز شهرستان‌ها'],['provinceBorders','مرز استان‌ها'],['countyCenters','مراکز شهرستان'],['provinceCenters','مراکز استان']];
 for(const [key,label] of opts){
   const layer=cfg.layers?.[key];
   const wrap=element('label',{},bar);const inp=element('input',{type:'checkbox'},wrap);inp.disabled=!assertLayer(layer);
   wrap.appendChild(document.createTextNode(label));
   if(assertLayer(layer)) { inp.checked=cfg.map.hasLayer(layer);inp.addEventListener('change',()=>{if(inp.checked)layer.addTo(cfg.map);else cfg.map.removeLayer(layer);}); }
   else wrap.title='لایهٔ معتبر بارگذاری نشده است';
 }
 const error=element('span',{className:'metstat-map-error',textContent:''},bar);
 function updateCounts(c){cfg.totalCount=c.total??cfg.totalCount;cfg.mappedCount=c.mapped??cfg.mappedCount;cfg.pendingCount=c.pending??cfg.pendingCount;
   countLabel.textContent=`گزارش: ${cfg.totalCount??0} | نقشه: ${cfg.mappedCount??0} | نیازمند بررسی: ${cfg.pendingCount??0}`;}
 updateCounts({total:cfg.totalCount??0,mapped:cfg.mappedCount??0,pending:cfg.pendingCount??0});
 function setMetadata(m){if(m.title)cfg.title=m.title;if(m.reportDate)cfg.reportDate=m.reportDate;if(m.province)cfg.province=m.province;}
 save.addEventListener('click',async()=>{save.disabled=true;error.textContent='';save.textContent='در حال تهیه PNG…';try{await exportPng(cfg);}catch(e){error.textContent=e?.message||'خطای خروجی PNG';}finally{save.disabled=false;save.textContent='ذخیره PNG';}});
 cfg.map.invalidateSize?.();return {toolbar:bar,updateCounts,setMetadata,exportPng:()=>exportPng(cfg),destroy:()=>bar.remove()};
}
return Object.freeze({install,exportPng});
});

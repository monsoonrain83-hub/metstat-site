/* MetStat r4: actual pointer-based drawing on simulated SVG canvas.
 * Historic P18 tools: pan, ruler, line/dash/arrow, cold/warm/occluded/stationary,
 * H/L, rectangle/circle/free polygon, dot, text, eraser, undo/redo.
 * DEMO ONLY: stored coordinates are normalized to SVG, NOT lon/lat or kilometres.
 * No network, remote data, HTML injection, external libraries or live file writes.
 */
(()=>{'use strict';
 const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
 const overlay=$('drawingOverlay'),toggle=$('drawingToggle'),tray=$('drawingTools');if(!overlay||!toggle||!tray)return;
 const store=new Map();let tool='pan',drag=null,route='',pending=null;
 const colorInput=$('drawColor'),widthInput=$('drawWidth'),opacityInput=$('drawOpacity');
 const frontTools=new Set(['cold','warm','occl','stat']);
 const lineTools=new Set(['solid','dash','arrow',...frontTools,'ruler']);
 function activePath(){return window.MetStatR3Preview?.getRoute?.()||'/monitoring-forecast/weather-models'}
 function entry(){const key=activePath();if(!store.has(key))store.set(key,{items:[],undo:[],redo:[]});return store.get(key)}
 const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
 function P(e){const r=overlay.getBoundingClientRect();return [(e.clientX-r.left)*1000/Math.max(r.width,1),(e.clientY-r.top)*600/Math.max(r.height,1)].map((v,i)=>clamp(v,0,i?600:1000))}
 function node(name,attrs={},text=null){const e=document.createElementNS(NS,name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!=null)e.textContent=String(text);return e}
 function snapshot(){const e=entry();e.undo.push(JSON.stringify(e.items));if(e.undo.length>80)e.undo.shift();e.redo.length=0}
 const xy=pts=>pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
 function lineStyle(i){return {'fill':'none','stroke':i.color||'#dc1937','stroke-width':i.width||3,'stroke-linejoin':'round','stroke-linecap':'round','opacity':i.opacity??1}}
 function cleanPoints(p){return p.filter(a=>Array.isArray(a)&&a.length===2&&a.every(v=>Number.isFinite(v))).map(a=>a.map(v=>Number(v.toFixed(2)))).slice(0,1000)}
 function geodist(a,b){return Math.hypot(b[0]-a[0],b[1]-a[1])}
 function drawSymbols(g,i){
  let seq=i.points||[];let len=0;let poly=[];
  for(let n=1;n<seq.length;n++){const a=seq[n-1],b=seq[n],d=geodist(a,b);if(d<1)continue;for(let t=32-len;t<d;t+=43){const v=t/d,xx=a[0]+(b[0]-a[0])*v,yy=a[1]+(b[1]-a[1])*v,ang=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
   poly.push({x:xx,y:yy,a:ang});}len=(len+d)%43;
  }
  const FRONT={cold:'#2878f7',warm:'#dc1937',occl:'#8e45d2',stat:'#2878f7'};
  poly.forEach((p,j)=>{const colour=FRONT[i.type]||'#fff',grp=node('g',{transform:`translate(${p.x.toFixed(1)} ${p.y.toFixed(1)}) rotate(${p.a.toFixed(1)}) scale(0.85 ${i.flip?-1:1})`});
   if(i.type==='cold'||(i.type==='occl'&&j%2===0)||(i.type==='stat'&&j%2===0))grp.appendChild(node('path',{d:'M -9 1 L 0 -15 L 9 1 Z',fill:i.type==='occl'?'#8e45d2':colour,stroke:'none'}));
   else grp.appendChild(node('path',{d:'M -9 0 A 9 9 0 0 1 9 0 Z',fill:i.type==='stat'?'#dc1937':colour,stroke:'none'}));
   g.appendChild(grp);
  });
 }
 function renderOne(item){
  const i=item.type,pts=cleanPoints(item.points||[]);if(!pts.length)return null;
  const g=node('g',{'data-draw-shape':i});
  if(i==='text'||i==='L'||i==='H'){
   const x=pts[0][0],y=pts[0][1];let text=i==='text'?String(item.text||'متن').slice(0,80):i;
   const t=node('text',{x,y,'font-size':item.font||24,'font-family':'Tahoma,Arial,sans-serif','font-weight':'900','text-anchor':'middle',fill:i==='H'?'#2878f7':i==='L'?'#dc1937':item.color,'paint-order':'stroke',stroke:'#fff','stroke-width':'.6'},text);g.append(t);return g;
  }
  if(i==='dot'){g.append(node('circle',{cx:pts[0][0],cy:pts[0][1],r:Math.max(4,item.width*2),fill:item.color,opacity:item.opacity}));return g}
  if(i==='rect'&&pts.length>=2){const a=pts[0],b=pts[pts.length-1];g.append(node('rect',{x:Math.min(a[0],b[0]),y:Math.min(a[1],b[1]),width:Math.abs(a[0]-b[0]),height:Math.abs(a[1]-b[1]),fill:item.color,'fill-opacity':item.opacity*.12,stroke:item.color,'stroke-width':item.width}));return g;}
  if(i==='circ'&&pts.length>=2){const a=pts[0],b=pts[pts.length-1];g.append(node('ellipse',{cx:a[0],cy:a[1],rx:Math.abs(a[0]-b[0]),ry:Math.abs(a[1]-b[1]),fill:item.color,'fill-opacity':item.opacity*.12,stroke:item.color,'stroke-width':item.width}));return g;}
  if(i==='free'&&pts.length>=3){g.append(node('path',{d:xy(pts)+'Z',...lineStyle(item),fill:item.color,'fill-opacity':item.opacity*.14}));return g;}
  if(pts.length<2)return null;
  const flat=Array.from(pts);if(item.straight&&flat.length>=2){const a=flat[0],b=flat.at(-1);flat.length=0;flat.push(a,b)}
  const paint=frontTools.has(i)?{'cold':'#2878f7','warm':'#dc1937','occl':'#8e45d2','stat':'#2878f7'}[i]:item.color;
  const style={...lineStyle({...item,color:paint})};if(i==='dash')style['stroke-dasharray']='12 8';
  g.appendChild(node('path',{d:xy(flat),...style}));
  if(frontTools.has(i))drawSymbols(g,{...item,points:flat});
  if(i==='arrow'){const a=flat.at(-2),b=flat.at(-1),angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
   g.append(node('path',{d:'M -13 -8 L 0 0 L -13 8',fill:'none',stroke:paint,'stroke-width':Math.max(item.width,2.5),transform:`translate(${b[0]} ${b[1]}) rotate(${angle})`}))}
  if(i==='ruler'){const a=flat[0],b=flat.at(-1),d=Math.hypot(a[0]-b[0],a[1]-b[1]);
   g.append(node('text',{x:(a[0]+b[0])/2,y:(a[1]+b[1])/2-9,'font-size':17,'font-weight':'bold','text-anchor':'middle',fill:'#fff',stroke:'#102c47','stroke-width':'.5'},`${Math.round(d)} px · نمایشی`));}
  return g;
 }
 function render(){overlay.replaceChildren();const capture=node('rect',{x:0,y:0,width:1000,height:600,fill:'transparent','pointer-events':'all','data-draw-capture':'1'});overlay.appendChild(capture);const state=entry();for(const it of state.items){const g=renderOne(it);if(g)overlay.append(g)}if(drag){const g=renderOne({...drag,points:drag.points});if(g){g.setAttribute('opacity','0.7');overlay.append(g)}}$('drawCount').textContent=new Intl.NumberFormat('fa-IR').format(state.items.length)+' ترسیم';}
 function setTool(t){if(!['pan','ruler','solid','dash','arrow','cold','warm','occl','stat','rect','circ','free','dot','text','L','H','eraser'].includes(t))return;tool=t;drag=null;overlay.dataset.active=String(t!=='pan');overlay.style.pointerEvents=t==='pan'?'none':'auto';overlay.style.touchAction=t==='pan'?'auto':'none';tray.querySelectorAll('[data-draw]').forEach(b=>{const on=b.dataset.draw===t;b.classList.toggle('is-active',on);b.setAttribute('aria-pressed',String(on))});render();}
 function makeItem(type,points){return {type,points:cleanPoints(points),color:colorInput.value,width:Number(widthInput.value),opacity:Number(opacityInput.value),font:Number($('drawFont').value),flip:$('drawFlip').checked,straight:$('drawStraight').checked};}
 function mouseDown(e){if(tool==='pan'||e.button!==0&&e.pointerType==='mouse')return;if(e.target!==overlay && e.target.ownerSVGElement!==overlay)return;const pt=P(e);
  if(tool==='eraser'){const state=entry();let best=-1,dist=35;state.items.forEach((it,j)=>{for(const p of it.points||[]){let dd=geodist(p,pt);if(dd<dist){dist=dd;best=j}}});if(best>=0){snapshot();state.items.splice(best,1);render()}return;}
  if(tool==='text'){pending=pt;$('drawTextInput').value='';if(!$('drawTextDialog').open)$('drawTextDialog').showModal();return;}
  if(tool==='L'||tool==='H'||tool==='dot'){snapshot();entry().items.push(makeItem(tool,[pt]));render();return;}
  drag=makeItem(tool,[pt,pt]);drag.pointer=e.pointerId;overlay.setPointerCapture(e.pointerId);render();e.preventDefault();
 }
 function mouseMove(e){if(!drag||drag.pointer!==e.pointerId)return;const pt=P(e);const pts=drag.points;
  if(lineTools.has(tool)&&!$('drawStraight').checked&&tool!=='ruler'||tool==='free'){
    if(geodist(pts.at(-1),pt)>4)pts.push(pt);else pts[pts.length-1]=pt;
  }else pts[pts.length-1]=pt;
  render();e.preventDefault();
 }
 function mouseUp(e){if(!drag||drag.pointer!==e.pointerId)return;const d=drag;drag=null;
  if(d.points.length>1&&geodist(d.points[0],d.points.at(-1))>3){snapshot();const {pointer,...item}=d;entry().items.push(item)}render();}
 function undo(){const e=entry();if(!e.undo.length)return;e.redo.push(JSON.stringify(e.items));e.items=JSON.parse(e.undo.pop());render()}
 function redo(){const e=entry();if(!e.redo.length)return;e.undo.push(JSON.stringify(e.items));e.items=JSON.parse(e.redo.pop());render()}
 function close(){tray.hidden=true;toggle.setAttribute('aria-expanded','false');}
 toggle.addEventListener('click',()=>{let on=tray.hidden;tray.hidden=!on;toggle.setAttribute('aria-expanded',String(on));if(on)tray.querySelector('[data-draw="pan"]')?.focus()});
 $('drawingClose').addEventListener('click',close);
 tray.addEventListener('click',e=>{const b=e.target.closest('[data-draw]');if(b)setTool(b.dataset.draw)});
 overlay.addEventListener('pointerdown',mouseDown);overlay.addEventListener('pointermove',mouseMove);
 overlay.addEventListener('pointerup',mouseUp);overlay.addEventListener('pointercancel',mouseUp);
 $('drawUndo').addEventListener('click',undo);$('drawRedo').addEventListener('click',redo);
 $('drawClear').addEventListener('click',()=>{if(!entry().items.length)return;snapshot();entry().items=[];render()});
 widthInput.addEventListener('input',()=>{$('drawWidthValue').textContent=widthInput.value+' px'});
 $('drawTextCancel').addEventListener('click',()=>{$('drawTextDialog').close();pending=null});
 $('drawTextConfirm').addEventListener('click',()=>{const text=$('drawTextInput').value.trim().slice(0,80);if(text&&pending){snapshot();entry().items.push({...makeItem('text',[pending]),text});render()}pending=null;$('drawTextDialog').close()});
 $('drawTextInput').addEventListener('keydown',e=>{if(e.key==='Enter'){$('drawTextConfirm').click();e.preventDefault()}});
 document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'&&!['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();if(e.shiftKey)redo();else undo()}});
 document.addEventListener('metstat:preview-route',e=>{route=e.detail?.path||activePath();drag=null;setTool('pan');close();render()});
 setTool('pan');
 window.MetStatR4Drawing=Object.freeze({getCount:()=>entry().items.length,getTool:()=>tool,source:'historic P18 fullscreen tool inventory',georeferenced:false});
})();
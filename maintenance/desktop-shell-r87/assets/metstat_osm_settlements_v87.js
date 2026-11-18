/* MetStat r87, additive named OSM nodes overlay. ODbL © OpenStreetMap contributors.
   Doesn't touch MAPF, SEATS, station identities, model physics, geo.json, or id_points CRC. */
(function(root){ 'use strict';
  const path='data/osm_settlements_v87.json';
  const state={ready:false,promise:null,index:new Map(),nodes:[],error:null};
  const norm=s=>String(s||'').normalize('NFKC').replace(/[\u200c\s\u0640]/g,'').replace(/ي/g,'ی').replace(/ك/g,'ک').toLowerCase();
  const bin=(a,b)=>Math.floor(a*2)+':'+Math.floor(b*2);
  const mercY=la=>{let v=Math.max(-85,Math.min(85,la))*Math.PI/180;return (1-Math.log(Math.tan(v)+1/Math.cos(v))/Math.PI)/2};
  const mercX=lo=>(lo+180)/360;
  const widthOK=(w,h)=>Number.isFinite(w)&&Number.isFinite(h)&&w>0&&h>0;
  function indexNodes(nodes){state.index.clear();state.nodes=nodes;for(const p of nodes){const key=bin(p[0],p[1]);let a=state.index.get(key);if(!a)state.index.set(key,a=[]);a.push(p)}state.ready=true;}
  function load(){if(state.promise)return state.promise;state.promise=fetch(path,{cache:'force-cache'}).then(r=>{if(!r.ok)throw Error('OSM places '+r.status);return r.json()}).then(d=>{
    if(!d||!Array.isArray(d.nodes)||!Array.isArray(d.fields)||d.fields.length!==8)throw Error('Invalid OSM schema');
    indexNodes(d.nodes);
    try{if(typeof root.nvDraw==='function')root.nvDraw(false)}catch(_){}
    try{if(typeof root.saDrawSoon==='function')root.saDrawSoon()}catch(_){}
    return state;
  }).catch(e=>{state.error=e.message;state.promise=null;console.warn('MetStat OSM overlay',e.message);return state});return state.promise;}
  function query(latMin,latMax,lonMin,lonMax){if(!state.ready)return[];const a=[];const x0=Math.floor(Math.max(23,latMin)*2),x1=Math.ceil(Math.min(42,latMax)*2),y0=Math.floor(Math.max(42,lonMin)*2),y1=Math.ceil(Math.min(66,lonMax)*2);
    for(let i=x0;i<=x1;i++)for(let j=y0;j<=y1;j++)for(const p of state.index.get(i+':'+j)||[])if(p[0]>=latMin&&p[0]<=latMax&&p[1]>=lonMin&&p[1]<=lonMax)a.push(p);
    return a;
  }
  function seatsCollision(p,existing){const nm=norm(p[2]),la=p[0],lo=p[1];
    // Only same-name nearby existing places suppress a new point. Existing sources always win.
    for(const q of existing){if(norm(q[0])!==nm)continue;const qla=+q[1],qlo=+q[2];if(Math.abs(la-qla)<0.014&&Math.abs((lo-qlo)*Math.cos(la*Math.PI/180))<0.014)return true;}
    return false;
  }
  function drawPoint(ctx,x,y,c,sz,k){ctx.save();ctx.lineWidth=.95*k; if(c===6){ctx.strokeStyle='#438452';ctx.fillStyle='#e6f2e4';ctx.fillRect(x-sz,y-sz,sz*2,sz*2);ctx.strokeRect(x-sz,y-sz,sz*2,sz*2)}else{
    ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=c<=1?'#164e87':c<=3?'#22779b':c===4?'#188b87':'#56758a';ctx.strokeStyle='#fcfdfe';ctx.fill();ctx.stroke()}
    ctx.restore();}
  function drawCore(ctx,W,H,bounds,project,scale,existing,occupied,maxPoint,flags){if(!widthOK(W,H))return 0; if(!state.ready){load();return 0;}
    let pts=query(bounds[0],bounds[1],bounds[2],bounds[3]);if(!pts.length)return 0;
    const ref=existing||[];const density=Math.max(8,Math.floor(W*H/950));let drawn=0,labels=0,limit=Math.max(90,Math.min(650,Math.floor(W*H/1700)));
    const cells=new Set();ctx.save();ctx.direction=(document.documentElement.lang==='en'?'ltr':'rtl');ctx.textAlign='center';ctx.textBaseline='bottom';
    for(const p of pts){const la=p[0],lo=p[1],name=ctx.direction==='ltr'?(p[3]||''):p[2];if((p[4]<=1&&!flags.city)||(p[4]>1&&!flags.vill)||!name||seatsCollision(p,ref))continue;
      const [x,y]=project(la,lo);if(x<2||x>W-2||y<2||y>H-2)continue;const c=p[4],sz=c<=1?3.8:c===4?2.5:c===6?2:2.1;
      if(drawn<(maxPoint||4000)){drawPoint(ctx,x,y,c,sz*scale,scale);drawn++;}
      if(labels>=limit)continue;
      if(c>=5&&W<850&&pts.length>400)continue; // low-priority labels at the densest town scales
      const key=Math.floor(x/48)+':'+Math.floor(y/23);if(cells.has(key))continue;
      const font=Math.round((c<=1?11.5:c===4?9.6:9.2)*scale);ctx.font=`${c<=1?700:550} ${font}px Tahoma,Vazirmatn,sans-serif`;
      const w=ctx.measureText(name).width+4*scale,top=y-4*scale-font;const rect=[x-w/2,top,x+w/2,y-3*scale];
      if(rect[0]<0||rect[2]>W||rect[1]<0||rect[3]>H)continue;
      if(occupied&&occupied.some(r=>rect[0]<r[2]&&rect[2]>r[0]&&rect[1]<r[3]&&rect[3]>r[1]))continue;
      cells.add(key);if(occupied)occupied.push(rect);
      ctx.fillStyle=c===6?'#287343':'#173c54';ctx.fillText(name,x,y-4*scale);labels++;
    }
    ctx.font=`${Math.round(9*scale)}px Tahoma,Arial,sans-serif`;ctx.textAlign="left";ctx.fillStyle="rgba(15,47,67,.8)";ctx.fillText("© OpenStreetMap contributors",8*scale,H-8*scale);ctx.restore();return drawn;
  }
  function drawNwp(ctx,W,H,k,x0,y0,scale,existing,occupied,flags){
    if(!Number.isFinite(k)||k<=0||W/k>2.6)return 0;const bounds=[y0-H/k,y0,x0,x0+W/k];
    return drawCore(ctx,W,H,bounds,(la,lo)=>[(lo-x0)*k,(y0-la)*k],scale,existing,occupied,4500,flags||{city:true,vill:true});
  }
  function drawSatellite(ctx,W,H,v,scale,existing,flags){
    if(!v||((v.zl??v.z)<9))return 0;const P=256*2**v.z;
    const lonOf=x=>x*360-180,latOf=y=>Math.atan(Math.sinh(Math.PI*(1-2*y)))*180/Math.PI;
    const b=[latOf(v.cy+H/2/P),latOf(v.cy-H/2/P),lonOf(v.cx-W/2/P),lonOf(v.cx+W/2/P)];
    if(b[3]-b[2]>2.6)return 0;
    return drawCore(ctx,W,H,b,(la,lo)=>[(mercX(lo)-v.cx)*P+W/2,(mercY(la)-v.cy)*P+H/2],scale,existing,[],3500,flags||{city:true,vill:true});
  }
  root.MetStatOSM=Object.freeze({load,drawNwp,drawSatellite,query,state,norm,indexNodes});
})(window);

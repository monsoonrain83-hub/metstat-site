import assert from 'node:assert/strict';
import {performance} from 'node:perf_hooks';
import {rasterForecastTile} from '../web/forecast/tile-raster.mjs';
function legacy(out,w,h,ax,ay,dx,dy,f,I,W0,H0,pal){
 const n=pal.length, WHITE=0xFFFFFFFF;
 for(let py=0;py<h;py++){ const v=(ay+py+0.5-dy)/f-0.5, j0=Math.max(0,Math.min(H0-1,Math.floor(v))), j1=Math.min(H0-1,j0+1), fy=Math.max(0,Math.min(1,v-j0)), r0=j0*W0, r1=j1*W0;
 for(let px=0;px<w;px++){ const u=(ax+px+0.5-dx)/f-0.5, i0=Math.max(0,Math.min(W0-1,Math.floor(u))), i1=Math.min(W0-1,i0+1), fx=Math.max(0,Math.min(1,u-i0));
 const a=I[r0+i0], b=I[r0+i1], c=I[r1+i0], d=I[r1+i1]; let val;
 if(a===b&&b===c&&c===d) val=a;
 else if(a<0||b<0||c<0||d<0){ const q=I[(fy>0.5?r1:r0)+(fx>0.5?i1:i0)]; val=q; }
 else val=Math.round((a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy);
 out[py*w+px]= val>=0&&val<n ? pal[val] : WHITE; } }
}
let seed=42;const rnd=()=>((seed=Math.imul(seed,1664525)+1013904223|0)>>>0)/4294967296;
let pixels=0;const pal=Uint32Array.from({length:32},(_,i)=>0xff000000|(i*723457));
for(let t=0;t<400;t++){
 const W=1+Math.floor(rnd()*80),H=1+Math.floor(rnd()*60),w=1+Math.floor(rnd()*120),h=1+Math.floor(rnd()*90);
 const I=Int16Array.from({length:W*H},()=>t%4===0?3:t%4===1?-1:Math.floor(rnd()*38)-3);
 const a=new Uint32Array(w*h),b=new Uint32Array(w*h),args=[w,h,Math.floor(rnd()*30),Math.floor(rnd()*30),rnd()*80-40,rnd()*80-40,[.25,.5,1,1.25,1.5,2,3.75,10][t%8],I,W,H,pal];
 legacy(a,...args);rasterForecastTile(b,...args);assert.deepEqual(a,b,`case ${t}`);pixels+=a.length;
}
const W=1200,H=900,w=1600,h=1200,I=Int16Array.from({length:W*H},(_,i)=>Math.floor(i/23)%33-1),a=new Uint32Array(w*h),b=new Uint32Array(w*h),args=[w,h,0,0,-123.4,-67.8,1.65,I,W,H,pal];
legacy(a,...args);rasterForecastTile(b,...args);assert.deepEqual(a,b);pixels+=a.length;
for(let i=0;i<4;i++){legacy(a,...args);rasterForecastTile(b,...args);}
const times=[[],[]];for(let i=0;i<12;i++)for(const k of i%2?[1,0]:[0,1]){let t=performance.now();(k?rasterForecastTile:legacy)(k?b:a,...args);times[k].push(performance.now()-t);}
const median=x=>x.sort((a,b)=>a-b)[Math.floor(x.length/2)];console.log(JSON.stringify({cases:401,pixels,legacyMs:median(times[0]),candidateMs:median(times[1]),scratchBytes:w*16}));

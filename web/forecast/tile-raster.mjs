// Exact legacy palette-index interpolation; only hoist horizontal geometry.
// Scratch arrays live for one paint, never retained by the forecast cache.
export function rasterForecastTile(out, w, h, ax, ay, dx, dy, f, I, W0, H0, pal){
  const n=pal.length, WHITE=0xFFFFFFFF;
  const left=new Int32Array(w), right=new Int32Array(w), frac=new Float64Array(w);
  for(let px=0;px<w;px++){
    const u=(ax+px+0.5-dx)/f-0.5, i0=Math.max(0,Math.min(W0-1,Math.floor(u)));
    left[px]=i0;right[px]=Math.min(W0-1,i0+1);frac[px]=Math.max(0,Math.min(1,u-i0));
  }
  for(let py=0;py<h;py++){
    const v=(ay+py+0.5-dy)/f-0.5, j0=Math.max(0,Math.min(H0-1,Math.floor(v))), j1=Math.min(H0-1,j0+1), fy=Math.max(0,Math.min(1,v-j0)), r0=j0*W0, r1=j1*W0, row=py*w;
    for(let px=0;px<w;px++){
      const i0=left[px],i1=right[px],fx=frac[px],a=I[r0+i0],b=I[r0+i1],c=I[r1+i0],d=I[r1+i1];let val;
      if(a===b&&b===c&&c===d) val=a;
      else if(a<0||b<0||c<0||d<0) val=I[(fy>0.5?r1:r0)+(fx>0.5?i1:i0)];
      else val=Math.round((a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy);
      out[row+px]=val>=0&&val<n?pal[val]:WHITE;
    }
  }
}

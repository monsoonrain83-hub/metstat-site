const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const read=d=>fs.readFileSync(d+'/assets/'+fs.readdirSync(d+'/assets').find(n=>n.startsWith('ms_r5_perf_core_')),'utf8');
(async()=>{
 const browser=await chromium.launch(),reports=[];
 try{
  for(const candidate of [false,true]){
   const source=read(candidate?'v88-candidate':'v88-baseline');
   const a=source.indexOf(candidate?'/** Byte- and count-bounded LRU':'function nvImg(url){'),b=source.indexOf('async function nvResolve(){',a);assert(a>=0&&b>a);
   const page=await browser.newPage();await page.setContent('<canvas width="1600" height="1200"></canvas>');await page.evaluate(()=>{window.NV={cache:new Map()}});await page.addScriptTag({content:source.slice(a,b)});
   const report=await page.evaluate(async candidate=>{
    const cx=document.querySelector('canvas').getContext('2d'),canvas=cx.canvas;let first,firstUrl;
    for(let i=0;i<30;i++){
      cx.fillStyle='rgb('+(i+1)+',20,30)';cx.fillRect(0,0,1600,1200);const url=canvas.toDataURL('image/png'),a=nvImg(url),b=nvImg(url);
      if(a!==b)throw Error('duplicate pending load');const img=await a;if(!img||img.naturalWidth!==1600||img.naturalHeight!==1200)throw Error('decode');
      if(i===0){first=img;firstUrl=url;}
    }
    const stats=candidate?NV_IMAGE_CACHE.stats():{entries:NV.cache.size,pending:0,estimatedBytes:NV.cache.size*1600*1200*4};
    cx.drawImage(first,0,0);const pixel=Array.from(cx.getImageData(0,0,1,1).data);
    if(pixel.join(',')!=='1,20,30,255')throw Error('evicted image damaged');
    const back=await nvImg(firstUrl);if(!back||back.naturalWidth!==1600)throw Error('reload failed');
    if(await nvImg('data:image/png;base64,broken')!==null)throw Error('invalid image accepted');
    return {candidate,...stats,decodedFrames:30,pixel};
   },candidate);
   reports.push(report);await page.close();
  }
  assert.equal(reports[0].entries,30);assert.equal(reports[1].entries,8);assert(reports[1].estimatedBytes<=64*1024*1024);
  fs.writeFileSync('v88-cache-report.json',JSON.stringify(reports,null,2));console.log(reports);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

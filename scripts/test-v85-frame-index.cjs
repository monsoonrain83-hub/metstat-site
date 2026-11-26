const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict'),{performance}=require('node:perf_hooks');
const read=(d)=>fs.readFileSync(d+'/'+fs.readdirSync(d).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
const old=read('v85-baseline/assets'),next=read('v85-candidate/assets');
const m=JSON.parse(fs.readFileSync('v85-manifest.json'));
function ctx(code){const x=vm.createContext({ON:{man:m}});const start=code.indexOf('const NV_RS={};'),end=code.indexOf('const NV_DROP=',start);vm.runInContext(code.slice(start,end)+'\nthis.rs=NV_RS;',x);return x;}
const a=ctx(old),b=ctx(next),keys=Object.keys(m.models);let checks=0;
function eq(k){const x=a.nvMeItems(k),y=b.nvMeItems(k);assert.equal(x.length,y.length);for(let i=0;i<x.length;i++)assert.equal(x[i],y[i]);checks++;return y;}
for(const k of [...keys,'missing',undefined])eq(k);
for(const k of keys){const run=m.models[k].prev?.run;if(run){a.rs[k]=b.rs[k]=run;eq(k);delete a.rs[k];delete b.rs[k];eq(k);}}
const k=keys.find(k=>a.nvMeItems(k).length>1);assert(k);const v=eq(k);v.reverse();v.pop();eq(k);
const altered={...m,items:m.items.slice().reverse(),items_prev:m.items_prev.slice().reverse()};a.ON.man=b.ON.man=altered;for(const k of keys)eq(k);altered.items.push({m:k,r:'me',p:'t2m',v:'test'});eq(k);altered.items.pop();eq(k);a.ON.man=b.ON.man=null;eq(k);a.ON.man=b.ON.man=m;
function bench(x){let n=0;const t=performance.now();for(let j=0;j<25;j++)for(const k of keys)n+=x.nvMeItems(k).length;return {ms:Math.round((performance.now()-t)*100)/100,rows:n};}
const orig=bench(a),opt=bench(b);assert.equal(orig.rows,opt.rows);const report={checks,models:keys.length,current:m.items.length,previous:m.items_prev.length,orig,opt};console.log(JSON.stringify(report,null,2));fs.writeFileSync('v85-index-report.json',JSON.stringify(report,null,2));

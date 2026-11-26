const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{performance}=require('node:perf_hooks');
const m=JSON.parse(fs.readFileSync(process.argv[4]));
function ctx(path){const s=fs.readFileSync(path,'utf8'),a=s.indexOf('const NV_RS={};'),b=s.indexOf('const NV_DROP=',a),c=s.indexOf('const NV_EU_INDEX='),d=s.indexOf('function nvEuItems('),e=s.indexOf('const NV_TC=',d);assert(a>=0&&b>a&&d>=0&&e>d);const x=vm.createContext({ON:{man:m}});vm.runInContext(s.slice(a,b)+s.slice(c<0?d:c,e)+'\nthis.rs=NV_RS;',x);return x;}
const a=ctx(process.argv[2]),b=ctx(process.argv[3]);const keys=Object.keys(m.models),params=[...new Set([...m.items,...m.items_prev].filter(i=>i.r==='eu').map(i=>i.p))];params.push('missing','z500L','z500H','z500V','z500W');let checks=0;
function eq(k,p){const x=a.nvEuItems(k,p),y=b.nvEuItems(k,p);assert.equal(x.length,y.length);for(let i=0;i<x.length;i++)assert.equal(x[i],y[i]);checks++;return y;}
for(const k of [...keys,'missing',undefined])for(const p of params)eq(k,p);
for(const k of keys){const run=m.models[k].prev?.run;if(run){a.rs[k]=b.rs[k]=run;for(const p of params)eq(k,p);delete a.rs[k];delete b.rs[k];}}
const item=m.items.find(i=>i.r==='eu'&&!/[LHVW]$/.test(i.p));assert(item);const v=eq(item.m,item.p);v.reverse();v.pop();eq(item.m,item.p);
const newM={...m,items:m.items.slice().reverse(),items_prev:m.items_prev.slice().reverse()};a.ON.man=b.ON.man=newM;eq(item.m,item.p);newM.items.push({...item,v:'test'});eq(item.m,item.p);newM.items.pop();eq(item.m,item.p);a.ON.man=b.ON.man=null;eq(item.m,item.p);a.ON.man=b.ON.man=m;
function bench(x){let n=0;const t=performance.now();for(let j=0;j<3;j++)for(const k of keys)for(const p of params)n+=x.nvEuItems(k,p).length;return{ms:Math.round((performance.now()-t)*100)/100,rows:n};}
const old=bench(a),next=bench(b);assert.equal(old.rows,next.rows);console.log(JSON.stringify({checks,models:keys.length,params:params.length,old,next},null,2));

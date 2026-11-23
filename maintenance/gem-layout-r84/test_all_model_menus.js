'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(process.argv[2], 'utf8');
const segment=(a,b)=>{const i=source.indexOf(a);assert(i>=0,`missing ${a}`);const j=source.indexOf(b,i+a.length);assert(j>i,`missing ${b}`);return source.slice(i,j)};
const pick=segment('function nvFillModels(){','function nvFillRun(){');
const elements={};
for(const id of ['fsTc','fsMods','fsRun','fsCb'])elements[id]={innerHTML:'',value:'',hidden:false,querySelector:()=>null,querySelectorAll:()=>[],getAttribute:()=>null};
const setup={
  NV:{s:{tc:'daily',m:'gfs',p:'p24'},entry:null}, NVF:{on:true}, ON:{man:{models:{gfs:{run:'2026111712',info:{tclass:'daily'}}},items:[]}},
  store:{get:()=>1}, NV_PLANNED:{daily:[]}, nvLabU:k=>k.toUpperCase(),nvLab:k=>k.toUpperCase(),
  nvModelsOf:()=>[['gfs',{run:'2026111712',info:{tclass:'daily'}}]],
  nvFill:(id,opts,v)=>{setup.captured=opts;return opts.find(x=>!x[2])?.[0]||''},nvFillRun:()=>{},
  $:id=>elements[id],NV_TC:[['daily','روزانه'],['weekly','هفتگی']],
  nvRunPrev:()=>null,nvRunSel:()=>'',nvMState:()=>'',onFmtRun:()=>'',
  nvPar:()=>null,nvLibList:()=>[],nvCbIds:()=>[],nvCbCur:()=>'',nvModelHas:()=>false,
};
vm.createContext(setup);vm.runInContext(pick,setup);
let n=0;
setup.nvFillModels();
let gem=setup.captured.find(o=>o[0]==='~gem');assert(gem&&gem[2]===true&&/فاقد داده/.test(gem[1]));n++;
setup.ON.man.models.gem={run:'2026111712',info:{tclass:'daily'}};
setup.nvFillModels();
gem=setup.captured.find(o=>o[0]==='~gem');assert(gem&&gem[2]===true&&/منتظر نقشه/.test(gem[1]));n++;
setup.nvModelsOf=()=>[['gfs',{run:'2026111712',info:{tclass:'daily'}}],['gem',setup.ON.man.models.gem]];
setup.nvFillModels();assert(!setup.captured.find(o=>o[0]==='~gem'));assert(setup.captured.some(o=>o[0]==='gem'));n++;
setup.NV.s.tc='weekly';setup.nvModelsOf=()=>[];setup.nvFillModels();assert(!setup.captured.find(o=>o[0]==='~gem'));n++;
// Fullscreen follows the exact same selector and must mark unavailable GEM as a non-button label.
assert(source.includes('html+=`<span class="fsHint" title="${known?')&&source.includes('GEM · ${known?"منتظر نقشه":"فاقد داده"}</span>`;'));n++;
console.log(`${n}/5 dropdown/fullscreen model-menu checks passed`);

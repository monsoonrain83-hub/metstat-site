'use strict';
const fs=require('fs'), assert=require('assert'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
function segment(a,b){ const st=src.indexOf(a); assert(st>=0,`missing ${a}`);const en=src.indexOf(b,st+a.length); assert(en>st,`missing ${b}`);return src.slice(st,en).trim(); }
const runSel=segment('function nvRunSel(m){','function nvRunIsPrev(m){');
const chips=segment('function wxModelChips(all){','function nvBarRefresh(){');
const mock=`
const NV_RS={};const ON={man:null};const NV={s:{tc:'daily',m:'gfs',p:'p24',fr:'2026111800'}};
function nvRunPrev(m){ const o=ON.man&&ON.man.models&&ON.man.models[m];return o&&o.prev&&o.prev.run?o.prev:null;}
${runSel}
function nvRunIsPrev(m){const pv=nvRunPrev(m);return !!(pv&&nvRunSel(m)===pv.run);}
function nvItemsSrc(m){return nvRunIsPrev(m)?((ON.man&&ON.man.items_prev)||[]).filter(i=>i.m===m):((ON.man&&ON.man.items)||[]);}
function nvMeItems(m){return (m?nvItemsSrc(m):(ON.man?ON.man.items:[])).filter(i=>i.r==='me'&&(!m||i.m===m)&&!/L$/.test(i.p));}
function nvModelsOf(tc){return Object.entries(ON.man&&ON.man.models||{}).filter(([k,o])=>((o.info&&o.info.tclass)||'daily')===tc&&nvMeItems(k).length);}
function nvLabU(k,o){return k.toUpperCase();}
function nvMState(){return 'ms-b';}
${chips}
({ON,NV,NV_RS,nvRunSel,nvRunIsPrev,wxModelChips,nvMeItems});`;
const v=vm.runInNewContext(mock);let count=0;
const gem={name:'GEM',run:'2026111712',info:{tclass:'daily'},status:'building'};
const gfs={name:'GFS',run:'2026111712',info:{tclass:'daily'},status:'complete'};
const item=(m,p='p24')=>({m,r:'me',p,v:'2026111800'});
function set(data){v.ON.man=data;v.NV_RS.gem=undefined;}
// 1: Model available, selected parameter/time not available: still listed.
set({models:{gfs,gem},items:[item('gfs'),item('gem','p3')],items_prev:[]});
assert.match(v.wxModelChips(false),/data-m="gem"/); count++;
// 2: GEM current run lacks tiles, previous run has tiles: previous becomes selectable.
set({models:{gfs,gem:{...gem,prev:{run:'2026111700'}}},items:[item('gfs')],items_prev:[item('gem')]});
assert.equal(v.nvRunSel('gem'),'2026111700');
assert.equal(v.nvMeItems('gem').length,1);assert.match(v.wxModelChips(),/GEM · قبلی/);count++;
// 3: A listed GEM model has no current nor previous ME tile: show honest unavailable placeholder.
set({models:{gfs,gem},items:[item('gfs')],items_prev:[]});
assert.doesNotMatch(v.wxModelChips(),/data-m="gem"/);assert.match(v.wxModelChips(),/GEM · منتظر نقشه/); count++;
// 4: Even absent model metadata is visible as missing data, never selectable.
set({models:{gfs},items:[item('gfs')],items_prev:[]});
assert.match(v.wxModelChips(),/GEM · فاقد داده/);assert.doesNotMatch(v.wxModelChips(),/data-m="gem"/);count++;
// 5: When model's current run has ME tiles, it beats previous run by default.
set({models:{gfs,gem:{...gem,prev:{run:'2026111700'}}},items:[item('gfs'),item('gem')],items_prev:[item('gem')]});
assert.equal(v.nvRunSel('gem'),'2026111712');count++;
// 6: Non-daily lists do not receive GEM placeholder.
v.NV.s.tc='weekly';assert.doesNotMatch(v.wxModelChips(),/GEM ·/);count++;
console.log(`${count}/6 GEM visibility and run-fallback tests passed`);

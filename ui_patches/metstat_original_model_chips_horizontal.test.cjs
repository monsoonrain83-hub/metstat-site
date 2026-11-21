const assert=require('node:assert/strict');
const originalChips={id:'fsMods',parentElement:null};
const popup={id:'popup',children:[originalChips]};
originalChips.parentElement=popup;
const top={children:[],appendChild(el){
  if(el.parentElement)el.parentElement.children=el.parentElement.children.filter(c=>c!==el);
  this.children.push(el);el.parentElement=this;
}};
const oldMenu={hidden:false};
let marker='';
const fullscreen={
 querySelector(selector){return {'#fsMods':originalChips,'.fsRow.fsA':top,'.fsModDd':oldMenu}[selector]||null;},
 setAttribute(k,v){if(k==='data-original-chips-horizontal')marker=v;}
};
global.document={readyState:'complete',body:{},getElementById:(id)=>id==='nvFs'?fullscreen:null};
global.window={};
require('./metstat_original_model_chips_horizontal.js');
assert.equal(originalChips.parentElement,top);
assert.equal(top.children.length,1);
assert.equal(popup.children.length,0);
assert.equal(oldMenu.hidden,true);
assert.equal(marker,'1');
assert.equal(typeof window.MetStatFixOriginalModelChips,'function');
assert.equal(window.MetStatFixOriginalModelChips(),true);
assert.equal(top.children.length,1,'Repeated fullscreen should never create duplicate model buttons');
console.log('Fullscreen original model chips relocation passed (7 checks)');

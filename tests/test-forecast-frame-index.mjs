import test from 'node:test';
import assert from 'node:assert/strict';
import {createForecastFrameIndex} from '../web/forecast/frame-index.mjs';
const row = (m,r,p,v) => ({m,r,p,v});
const fixture = () => {
  let previous = new Set();
  let m = {items:[row('a','me','t2m','1'),row('b','me','t2m','1'),row('a','me','t2mL','1'),row('a','me','t2mH','1'),row('a','eu','z500','1'),row('a','eu','z500L','1'),row('a','eu','z500H','1'),row('a','eu','z500V','1'),row('a','eu','z500W','1'),row('b','eu','z500','1'),row('a','eu','z500','2')],items_prev:[row('a','me','t2m','0'),row('a','eu','z500','0'),row('b','eu','z500','0')]};
  const idx = createForecastFrameIndex(()=>m,k=>previous.has(k));
  return {idx,previous,get m(){return m},set m(value){m=value}};
};
test('ME excludes only L; EU excludes L/H/V/W; exact model/parameter and order',()=>{
  const {idx,m}=fixture();assert.deepEqual(idx.middleEast('a'),[m.items[0],m.items[3]]);assert.deepEqual(idx.middleEast(),[m.items[0],m.items[1],m.items[3]]);assert.deepEqual(idx.europe('a','z500'),[m.items[4],m.items[10]]);assert.deepEqual(idx.europe('a','z500H'),[]);assert.deepEqual(idx.europe('missing','z500'),[]);
});
test('previous run is selected separately for each model',()=>{const {idx,m,previous}=fixture();previous.add('a');assert.deepEqual(idx.middleEast('a'),[m.items_prev[0]]);assert.deepEqual(idx.europe('a','z500'),[m.items_prev[1]]);assert.deepEqual(idx.europe('b','z500'),[m.items[9]]);assert.deepEqual(idx.middleEast(),[m.items[0],m.items[1],m.items[3]]);});
test('fresh arrays and original row identities',()=>{const {idx,m}=fixture();let a=idx.europe('a','z500');assert.equal(a[0],m.items[4]);a.reverse();a.pop();assert.deepEqual(idx.europe('a','z500'),[m.items[4],m.items[10]]);idx.middleEast('a').length=0;assert.equal(idx.middleEast('a').length,2);});
test('array replacement, length change, root replacement, explicit invalidation',()=>{const f=fixture();const {idx}=f;assert.equal(idx.middleEast('a').length,2);f.m.items=f.m.items.slice().reverse();assert.equal(idx.middleEast('a')[0].p,'t2mH');f.m.items.push(row('a','me','x','3'));assert.equal(idx.middleEast('a').length,3);f.m.items.pop();assert.equal(idx.middleEast('a').length,2);f.m.items[0]=row('a','me','y','3');f.m={...f.m};assert.equal(idx.middleEast('a').length,3);f.m.items[0]=row('b','me','y','3');idx.invalidate();assert.equal(idx.middleEast('a').length,2);});
test('no manifest and missing previous arrays',()=>{const f=fixture();f.m=null;assert.deepEqual(f.idx.middleEast('a'),[]);assert.deepEqual(f.idx.europe('a','z500'),[]);f.m={items:[]};f.previous.add('a');assert.deepEqual(f.idx.middleEast('a'),[]);assert.deepEqual(f.idx.europe('a','z500'),[]);});

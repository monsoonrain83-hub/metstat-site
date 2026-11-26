const test=require('node:test');
const assert=require('node:assert/strict');
const {markedScope}=require('../web/online/rainfall_name_scope_v75.js');
const provinces=['فارس','گلستان','مازندران','گیلان'];
const key=x=>String(x).replace(/\s+/gu,'');
test('province word inside station name stays intact',()=>{
 for(const name of ['شهرک گلستان شیراز','شهرک گلستان','پارک ملی گلستان','گلستان شیراز'])
  assert.deepEqual(markedScope(name,provinces,key),{name,province:''});
});
test('explicit scope markers split full province only',()=>{
 for(const name of ['شهرک گلستان شیراز - فارس','شهرک گلستان شیراز استان فارس'])
  assert.deepEqual(markedScope(name,provinces,key),{name:'شهرک گلستان شیراز',province:'فارس'});
 assert.deepEqual(markedScope('رشت-استانداری',provinces,key),{name:'رشت-استانداری',province:''});
});

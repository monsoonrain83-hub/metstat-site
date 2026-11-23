const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const src=fs.readFileSync(require('node:path').join(__dirname,'../app.js'),'utf8');
const first=src.indexOf('const offlineDocument=');
const last=src.indexOf('function periodFromRoute(',first);
assert(first>=0&&last>first,'routing helpers are present');
const code=src.slice(first,last);
const target='/ava-studio/photo-editor';
function make({scheme,throwHash=false}){
 const location={protocol:scheme,pathname:'/external/file/1',_hash:''};
 Object.defineProperty(location,'hash',{get(){return this._hash;},set(value){if(throwHash)throw new DOMException('restricted','SecurityError');this._hash='#'+String(value).replace(/^#/,'')}});
 let pushCalls=0;
 const env={location,history:{pushState(){pushCalls++;throw new DOMException('opaque origin','SecurityError')}},byPath:new Map([[target,true],['/monitoring-forecast/weather-models',true]]),canonical:s=>s,DOMException};
 vm.createContext(env);vm.runInContext(code+';globalThis.helpers={getRouteFromLocation,changeUrl,offlineDocument}',env);
 return {location,helpers:env.helpers,pushCalls:()=>pushCalls};
}
for(const scheme of ['content:','file:','about:','data:']){
 const {location,helpers,pushCalls}=make({scheme});
 assert.equal(helpers.offlineDocument(),true);
 assert.equal(helpers.getRouteFromLocation(),'/monitoring-forecast/weather-models');
 assert.doesNotThrow(()=>helpers.changeUrl(target));
 assert.equal(pushCalls(),0,'never invoke History.pushState for '+scheme);
 if(scheme==='content:')assert.equal(location.hash,'','Android content URL stays unchanged');
 else{assert.equal(location.hash,'#'+target);assert.equal(helpers.getRouteFromLocation(),target)}
}
const restricted=make({scheme:'file:',throwHash:true});
assert.doesNotThrow(()=>restricted.helpers.changeUrl(target));
console.log('PASS offline route navigation for content://, file://, about:, data: and restricted hash changes');

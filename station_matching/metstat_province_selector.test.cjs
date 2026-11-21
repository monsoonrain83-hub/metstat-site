const assert=require('node:assert/strict');
const {mount,provinces}=require('./metstat_province_selector.js');
const saved=new Map();
const storage={getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,v)};
let doc;
class El{
 constructor(tag){this.tagName=tag;this.children=[];this.events={};this.className='';this.ownerDocument=doc;this.parent=null;this.checked=false;this.textContent='';}
 appendChild(child){child.parent=this;this.children.push(child);return child;}
 addEventListener(name,fn){this.events[name]=fn;}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);}
 querySelector(selector){const name=selector.startsWith('.')?selector.slice(1):selector;for(const c of this.children){if(c.className.split(' ').includes(name))return c;const n=c.querySelector(selector);if(n)return n;}return null;}
}
doc={createElement:tag=>new El(tag),defaultView:{localStorage:storage}};
const box=new El('div'),events=[];
const one=mount({container:box,document:doc,onChange:x=>events.push(x)});
assert.equal(provinces.length,31);
assert.deepEqual(one.getSelected(),[]);
assert.equal(events.length,1);
one.setSelected(['خراسان رضوی','خراسان شمالی','غیرواقعی']);
assert.deepEqual(one.getSelected(),['خراسان رضوی','خراسان شمالی']);
assert.deepEqual(JSON.parse(storage.getItem('metstat.rain.selectedProvinces')),['خراسان رضوی','خراسان شمالی']);
assert.throws(()=>mount({container:box,document:doc}),/already mounted/);
one.destroy();
const two=mount({container:box,document:doc});
assert.deepEqual(two.getSelected(),['خراسان رضوی','خراسان شمالی']);
const details=two.element.children[0],panel=details.children[1],all=panel.children[0].children[0];
all.checked=true;all.events.change();
assert.deepEqual(two.getSelected(),[]);
assert.equal(storage.getItem('metstat.rain.selectedProvinces'),'[]');
two.destroy();
const three=mount({container:box,document:doc,storage:{getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}}});
assert.deepEqual(three.getSelected(),[]);
three.destroy();
console.log('Province selector mount/persistence regression passed (9 checks)');

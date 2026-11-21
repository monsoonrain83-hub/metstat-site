/* Opt-in province selector. Mount beside the rainfall text input; do not duplicate the existing Search button. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MetStatProvinceSelector=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const provinces=['آذربایجان شرقی','آذربایجان غربی','اردبیل','اصفهان','البرز','ایلام','بوشهر','تهران','چهارمحال و بختیاری','خراسان جنوبی','خراسان رضوی','خراسان شمالی','خوزستان','زنجان','سمنان','سیستان و بلوچستان','فارس','قزوین','قم','کردستان','کرمان','کرمانشاه','کهگیلویه و بویراحمد','گلستان','گیلان','لرستان','مازندران','مرکزی','هرمزگان','همدان','یزد'];
function mount({container,document:doc,onChange,initial=[]}){
 if(!container)throw Error('container required');doc=doc||container.ownerDocument;const wrap=doc.createElement('div');wrap.className='metstat-province-scope';
 const details=doc.createElement('details'),summary=doc.createElement('summary');summary.textContent='محدوده جست‌وجو: کل ایران';details.appendChild(summary);
 const panel=doc.createElement('div');panel.className='metstat-province-options';const chosen=new Set(initial.filter(x=>provinces.includes(x)));
 const all=doc.createElement('input');all.type='checkbox';all.checked=chosen.size===0;const allLabel=doc.createElement('label');allLabel.textContent='کل ایران';allLabel.appendChild(all);panel.appendChild(allLabel);
 const checks=[];
 function emit(){all.checked=chosen.size===0;summary.textContent=chosen.size?'محدوده: '+chosen.size+' استان':'محدوده جست‌وجو: کل ایران';if(onChange)onChange([...chosen]);}
 all.addEventListener('change',()=>{if(all.checked){chosen.clear();for(const [p,input] of checks)input.checked=false;}else{all.checked=chosen.size===0;}emit();});
 for(const p of provinces){const label=doc.createElement('label');label.textContent=p;const input=doc.createElement('input');input.type='checkbox';input.checked=chosen.has(p);input.addEventListener('change',()=>{input.checked?chosen.add(p):chosen.delete(p);emit();});label.appendChild(input);panel.appendChild(label);checks.push([p,input]);}
 details.appendChild(panel);wrap.appendChild(details);container.appendChild(wrap);emit();
 return {element:wrap,getSelected:()=>[...chosen],setSelected(items){chosen.clear();for(const p of items||[])if(provinces.includes(p))chosen.add(p);for(const [p,input] of checks)input.checked=chosen.has(p);emit();},destroy(){wrap.remove();}};
}
return {provinces,mount};
});

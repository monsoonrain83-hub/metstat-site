/** One owner for R5 parameter picker DOM. No timers, observers or global state. */
export function createParameterPicker() {
  const rendered = new WeakMap();
  return function render(host, {parameters:ps, categories, secondary, selected, group, secondaryGroups, text, translate}) {
    const cats=categories.slice().sort((a,b)=>(a.o||0)-(b.o||0));
    const groups=[];
    if(secondary){
      const used=new Set();
      for(const [title,ids] of secondaryGroups){const L=ps.filter(p=>p.cat==='sc'&&ids.includes(p.id.replace(/(6|24|acc)$/, '')));if(L.length){groups.push(['sc:'+title,title,L]);L.forEach(p=>used.add(p.id));}}
      const rem=ps.filter(p=>p.cat==='sc'&&!used.has(p.id));if(rem.length)groups.push(['sc:other',text('سایر نقشه‌های ثانویه','Other derived maps'),rem]);
    }else{
      for(const cat of cats){if(cat.id==='sc')continue;const L=ps.filter(p=>p.cat===cat.id).sort((a,b)=>(a.o||0)-(b.o||0));if(L.length)groups.push([cat.id,text(cat.fa||cat.id,cat.en||translate(cat.fa||cat.id)),L]);}
      const found=new Set(groups.flatMap(g=>g[2].map(p=>p.id)));const extra=ps.filter(p=>p.cat!=='sc'&&!found.has(p.id));if(extra.length)groups.push(['others',text('سایر پارامترها','Other parameters'),extra]);
    }
    const current=groups.find(g=>g[2].some(p=>p.id===selected));
    if(groups.length&&(group===null||(group!==''&&!groups.some(g=>g[0]===group))))group=current?current[0]:groups[0][0];
    const view={label:text('نوع تولید نقشه','Map generation mode'),tabs:[['m',text('تولید مستقیم','Direct fields'),!secondary,false],['s',text('تولید ثانویه','Derived fields'),secondary,!ps.some(p=>p.cat==='sc')]],hint:groups.length?'':text('برای مدل فعلی پارامتری در این بخش موجود نیست.','No parameters in this group for the selected model.'),groups:groups.map(([key,label,L])=>[key,text(label,translate(label))+' ('+L.length+')',group===key,group===key?L.map(p=>[p.id,text(p.fa||p.id,p.en||translate(p.fa||p.id)),p.id===selected]):[]])};
    const signature=JSON.stringify(view),prev=rendered.get(host);
    if(prev&&prev.signature===signature&&prev.html===host.innerHTML)return group;
    const doc=host.ownerDocument,fragment=doc.createDocumentFragment();
    const button=(cls,key,val,label,attr,state)=>{const b=doc.createElement('button');b.type='button';b.className=cls;b.dataset[key]=val;b.setAttribute(attr,String(state));b.textContent=label;return b;};
    const tabs=doc.createElement('div');tabs.className='msR5-param-tabs';tabs.setAttribute('role','group');tabs.setAttribute('aria-label',view.label);
    for(const [kind,label,pressed,disabled] of view.tabs){const b=button('msR5-param-tab','r5kind',kind,label,'aria-pressed',pressed);b.disabled=disabled;tabs.append(b);}fragment.append(tabs);
    if(view.hint){const hint=doc.createElement('p');hint.className='hint';hint.textContent=view.hint;fragment.append(hint);}
    for(const [key,label,opened,items] of view.groups){const section=doc.createElement('section');section.className='msR5-param-group';section.append(button('msR5-param-head','r5group',key,label,'aria-expanded',opened));if(opened){const list=doc.createElement('div');list.className='msR5-param-items';for(const [id,label,pressed] of items)list.append(button('msR5-param-choice','r5param',id,label,'aria-pressed',pressed));section.append(list);}fragment.append(section);}
    host.replaceChildren(fragment);rendered.set(host,{signature,html:host.innerHTML});return group;
  };
}

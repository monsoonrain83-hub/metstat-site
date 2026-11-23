/* MetStat vNext r4: user/admin-panel VISUAL SIMULATION only.
   Exact historic r97 nomenclature; no auth.php calls, cookies, credential collection,
   account creation, role escalation or persistence. All roles are demo banners. */
(()=>{'use strict';
 const $=id=>document.getElementById(id);
 const holder=$('accountControl'),btn=$('accountToggle'),drop=$('accountDropdown');
 if(!holder||!btn||!drop)return;
 let role='guest',lastNonAccount='/monitoring-forecast/weather-models';
 const paths={account:'/account',login:'/account/login',register:'/account/register',favorites:'/account/favorites',profile:'/account/profile',admin:'/account/admin',approval:'/account/station-approval'};
 const pages=[['/account/login','ورود'],['/account/register','ثبت‌نام'],['/account/favorites','علاقه‌مندی‌ها'],['/account/profile','ویرایش حساب و تغییر رمز'],['/account/admin','پنل مدیر'],['/account/station-approval','تأیید آمار ماهانهٔ ایستگاه‌ها']];
 const create=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e};
 const entries={
  '/account/login':{hint:'ورود آزمایشی · فرم غیرفعال؛ هیچ رمز یا نام کاربری ارسال نمی‌شود',fields:[['نام کاربری / ایمیل','text'],['رمز عبور','password']],actions:['ورود (غیرفعال)','بازیابی گذرواژه (غیرفعال)']},
  '/account/register':{hint:'ثبت‌نام نمایشی · بدون ثبت اطلاعات',fields:[['نام و نام خانوادگی','text'],['ایمیل','email'],['شماره تماس','text'],['رمز عبور','password']],actions:['ایجاد حساب (غیرفعال)']},
  '/account/favorites':{hint:'علاقه‌مندی‌ها · نمونه ظاهر، هیچ مورد واقعی بارگذاری نشده',sections:['نقشه‌های نشان‌شده','ایستگاه‌های منتخب','مناطق مورد علاقه'],actions:['افزودن علاقه‌مندی (نمایشی)']},
  '/account/profile':{hint:'ویرایش حساب و تغییر رمز · ورود واقعی لازم است',fields:[['نام نمایشی','text'],['ایمیل','email'],['رمز عبور فعلی','password'],['رمز عبور جدید','password']],actions:['ذخیره مشخصات (غیرفعال)']},
  '/account/admin':{hint:'پنل مدیر · فقط نقش نمونه، بدون دسترسی مدیریتی واقعی',sections:['مدیریت کاربران','مدیریت داده‌ها و آپلود','محتوا و صفحات','گزارش عملیات و امنیت'],actions:['باز کردن مدیریت واقعی (غیرفعال)']},
  '/account/station-approval':{hint:'تأیید آمار ماهانه ایستگاه‌ها · جدول بدون رکورد واقعی',sections:['موارد منتظر بررسی: بدون داده متصل','آمار تأییدشده: بدون داده متصل','گزارش رد و اصلاح: بدون داده متصل'],actions:['تأیید داده (غیرفعال)']}
 };
 function detail(route){
  const box=$('accountStageDetails');if(!box)return;
  box.replaceChildren();const cfg=entries[route];if(!cfg)return;
  const badge=create('p',cfg.hint);badge.className='account-detail-hint';box.appendChild(badge);
  if(cfg.fields){const fields=document.createElement('div');fields.className='account-detail-fields';for(const [name,type] of cfg.fields){
   const wrap=document.createElement('label');wrap.textContent=name;const input=document.createElement('input');input.type=type;input.disabled=true;input.placeholder='نمونه · ورود اطلاعات غیرفعال';input.autocomplete='off';wrap.appendChild(input);fields.appendChild(wrap);
  }box.appendChild(fields)}
  if(cfg.sections){const sections=document.createElement('div');sections.className='account-detail-sections';for(const title of cfg.sections){const item=create('div',title);item.className='account-detail-section';item.title='بدون اتصال به داده واقعی';sections.appendChild(item)}box.appendChild(sections)}
  for(const title of cfg.actions){const btn=create('button',title);btn.type='button';btn.disabled=true;btn.className='account-detail-submit';box.appendChild(btn)}
 }

 function render(){
  drop.replaceChildren();const head=create('div','حساب کاربری MetStat · فقط پیش‌نمایش');head.className='account-dropdown-head';drop.appendChild(head);
  const current=create('div',role==='guest'?'وضعیت: مهمان':role==='user'?'وضعیت: کاربر نمایشی':'وضعیت: مدیر نمایشی');current.className='account-demo-role';drop.appendChild(current);
  for(const [p,name] of [['/account','نمای کلی حساب'],...pages]){
   const a=create('a',name);a.href=p;a.dataset.route=p;a.className='account-menu-link';if(role!=='admin'&&(p===paths.admin||p===paths.approval))a.title='فقط با حالت مدیر نمایشی';drop.appendChild(a);
  }
  const sep=document.createElement('div');sep.className='account-menu-separator';drop.appendChild(sep);
  for(const [key,text] of [['user-demo','پیش‌نمایش پنل کاربر'],['admin-demo','پیش‌نمایش پنل مدیر'],['guest-demo','خروج از حالت نمایشی']]){
   const b=create('button',text);b.type='button';b.dataset.accountAction=key;b.className='account-demo-action';drop.appendChild(b);
  }
  $('accountStatus').textContent=role==='guest'?'حساب کاربری':role==='user'?'کاربر (نمایشی)':'مدیر (نمایشی)';
  const view=$('accountView');
  if(view){const route=window.MetStatR3Preview?.getRoute?.()||'/account';const page=(window.MetStatRoutes||[]).find(x=>x.path===route)||null;
   $('accountStageTitle').textContent=page?.group==='حساب کاربری'?page.title:'پنل کاربری';
   $('accountStageDescription').textContent='این بخش برای بررسی چیدمان بازسازی شده؛ احراز هویت، ثبت‌نام، رمزها و حقوق مدیر به سرور متصل نیست.';
   const links=$('accountStageLinks');links.replaceChildren();for(const [p,name] of pages){
    const a=create('a',name);a.href=p;a.dataset.route=p;links.appendChild(a);
   }
   detail(route);
  }
 }
 function close(){drop.hidden=true;btn.setAttribute('aria-expanded','false')}
 btn.addEventListener('click',e=>{e.stopPropagation();const open=drop.hidden;render();drop.hidden=!open;btn.setAttribute('aria-expanded',String(open))});
 document.addEventListener('click',e=>{
  const action=e.target.closest('[data-account-action]');if(action){e.preventDefault();setRole(action.dataset.accountAction);close();return}
  if(!holder.contains(e.target))close();
 });
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!drop.hidden){close();btn.focus()}});
 document.addEventListener('metstat:preview-route',ev=>{
  const p=ev.detail?.path;if(p&&!p.startsWith('/account'))lastNonAccount=p;
  if(p?.startsWith('/account')){render();close()}
 });
 function setRole(value){
  if(!['user-demo','admin-demo','guest-demo'].includes(value))return;
  role=value==='user-demo'?'user':value==='admin-demo'?'admin':'guest';
  render(); // Labelled simulation; never set real auth flags.
  const route=window.MetStatR3Preview?.getRoute?.();
  if(role==='guest'&&route?.startsWith('/account/admin')){$('accountStageDescription').textContent='برای بررسی ظاهر مدیر، گزینه «پیش‌نمایش پنل مدیر» را انتخاب کن.';}
 }
 window.MetStatR4Account=Object.freeze({setRole,getRole:()=>role,connected:false});
 // Initial mode is deliberately guest and mock-only.
 render();
})();
/* r5 complete-site visual review: distinct information architecture and page surfaces.
   No remote loading, no invented meteorological measurements. */
(()=>{'use strict';
const all=window.MetStatRoutes||[];
const byPath=new Map(all.map(p=>[p.path,p]));
const feature=document.getElementById('featureR5'),studio=document.getElementById('studioR5');
const stage=document.getElementById('mapStage');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const descriptions={
 'meteo':['نقطه یا ایستگاه','پیش‌بینی دما، بارش و باد','نمودار قائم و زمان','مقایسه مدل‌ها'],
 'station':['فیلتر استان و شهر','جدول آخرین مشاهده','نمودار ساعتی','وضعیت تأخیر داده'],
 'satellite':['کانال مرئی و فروسرخ','انتخاب ماهواره یا رادار','انیمیشن فریم‌ها','افزودن لایه جغرافیایی'],
 'indices':['سری زمانی شاخص','آنومالی و نرمال','همبستگی و تحلیل','دوره مبنا'],
 'climate':['ماه و فصل هدف','منبع داده معتبر','آنومالی و روند','مقایسه بازه‌ها'],
 'flood':['تجمع بارش ۱ تا ۲۴ ساعت','حوضه آبریز','شیب و کاربری اراضی','مقایسه ECMWF و GFS'],
 'isohyet':['ورود داده ایستگاهی','تطبیق نام ایستگاه','درون‌یابی و QC','دانلود نقشه و جدول'],
 'applied':['منطقه منتخب','پارامترهای کاربردی','بازه زمانی','توضیح و هشدار'],
 'hazard':['پدیده هدف','بازه و شدت','منطقه صدور','محصول هشدار'],
 'synoptic':['MSLP و ترازهای فشار','ترسیم جبهه و H/L','نقشه‌های ترکیبی','ابزار اندازه‌گیری'],
 'atlas':['انتخاب ایستگاه یا استان','نمودار نرمال و روند','آمار بلندمدت','نمای نقشه'],
 'drought':['شاخص SPI/SPEI','پنجره تجمع','نقشه و نمودار','مقایسه دوره مبنا'],
 'charts':['انتخاب شاخص و متغیر','نمای سری زمانی','تحلیل آماری','جدول خروجی'],
 'upload':['انتخاب نقشه و منبع','زمین‌مرجع و تطبیق','ترکیب و مقایسه','خروجی PNG/GeoTIFF'],
 'convection':['CAPE و CIN','شاخص‌های همرفت','مقایسه مکانی','آستانه هشدار'],
 'terrain':['DEM و مرز حوضه','مدل و متغیر خام','روش تصحیح ارتفاع','بازبینی نقشه اصلاح‌شده'],
 'lightning':['فریم‌های رعدوبرق','انتخاب بازه','تراکم مکانی','نقشه خروجی'],
 'convert':['انتخاب فرمت ورودی','تنظیم واحد/رزولوشن','بازبینی فایل','دریافت خروجی']
};
function render(path){const p=byPath.get(path);if(!p)return;
 const isStudio=p.group==='استودیو آوا',show=!['forecast','custom','home','account'].includes(p.kind)&&!isStudio;
 feature.hidden=!show;studio.hidden=!isStudio;feature.classList.toggle('map-kind',['synoptic','isohyet','flood','station','satellite','lightning','convection','terrain','upload','hazard'].includes(p.kind));stage.dataset.stage=isStudio?'studio':show?'feature':'map';
 if(!show){feature.replaceChildren();return}
 const root=all.filter(q=>q.parent_path===p.path);
 const entries=root.length?root:[];
 const tiles=entries.length?entries.map(x=>({title:x.title,path:x.path,note:'باز کردن صفحه مستقل'})):(descriptions[p.kind]||['ورودی و پارامتر','نمای خروجی','گزینه‌های تحلیل','تنظیمات و دریافت']).map((x,i)=>({title:x,note:i===0?'ورودی و بازهٔ انتخابی':i===3?'خروجی پس از اتصال موتور واقعی':'پنل شبیه‌سازی محصول'}));
 feature.innerHTML='<span class="feat-pill">UI PREVIEW / NO LIVE DATA</span><h2 class="feat-title">'+esc(p.title)+'</h2><p class="feat-note">'+esc(p.description)+' · این صفحه قالب اختصاصی بررسی UX است و داده هواشناسی واقعی ارائه نمی‌کند.</p><div class="feat-grid">'+tiles.map(x=>'<article class="feat-card"><strong>'+esc(x.title)+'</strong><small>'+esc(x.note)+'</small>'+(x.path?'<a href="'+esc(x.path)+'" data-route="'+esc(x.path)+'">باز کردن این زیرصفحه</a>':'<span class="feat-pill">اتصال موتور: انجام نشده</span>')+'</article>').join('')+'</div>';
}
document.addEventListener('metstat:preview-route',e=>render(e.detail.path));
const p=window.MetStatR3Preview?.getRoute?.()||'/monitoring-forecast/weather-models';render(p);
})();
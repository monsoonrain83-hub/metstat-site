import asyncio,json,pathlib
from playwright.async_api import async_playwright
ROOT=pathlib.Path('/mnt/data/metstat_r87_work/public');h=(ROOT/'index.html').read_text().replace('<link rel="stylesheet" href="assets/metstat_desktop_shell_v87.css?v=87">','<style>'+ (ROOT/'assets/metstat_desktop_shell_v87.css').read_text()+'</style>')
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for size,mob in [(1440,False),(390,True)]:
   ctx=await b.new_context(viewport={'width':size,'height':870 if size>500 else 844},device_scale_factor=1,is_mobile=mob,has_touch=mob)
   p=await ctx.new_page();await p.set_content(h,wait_until='domcontentloaded',timeout=20000)
   await p.evaluate('''() => {
    const n=document.getElementById('msNavR1');n.innerHTML=['پایش و پیش‌بینی','نقشه‌های مدل‌های جهانی','هواشناسی کوهستان','تهیهٔ نقشه‌های هم‌بارش','جعبه‌ابزار هواشناسی','پایش دقت مدل‌ها','اطلس اقلیمی','لایه‌های جغرافیایی'].map((s,i)=>`<button type="button" class="btn ${i===0?'main':''}">${s}</button>`).join('');
    const a=document.getElementById('onApp');a.hidden=false; const side=document.getElementById('onAside');side.innerHTML=`<section class="card" style="padding:14px"><h3>تنظیمات نقشه</h3><label>مدل<select><option>GEM GDPS</option></select></label><label>پارامتر<select><option>بارش ۲۴ ساعته</option></select></label><label>ساعت<select><option>00 UTC</option></select></label><button type="button">تنظیم لایه‌ها</button></section>`;
    const main=a.querySelector('main');main.innerHTML=`<section class="card" style="padding:12px;min-height:680px"><h2>تحلیل نقشه‌های آنلاین</h2><div style="height:590px;border:1px solid #cbd5e1;border-radius:10px;background:linear-gradient(135deg,#deefff,#ebf6ff);display:flex;align-items:center;justify-content:center;font-size:24px;color:#526e86">محل نمایش نقشه / نمودار</div></section>`;
   }''')
   v=await p.evaluate('''() => {const box=id=>{let r=document.getElementById(id).getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}};return{viewport:innerWidth,nav:box('msNav'),main:document.querySelector('#onApp main').getBoundingClientRect().toJSON(),side:box('onAside'),app:box('onApp'),overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth}}''')
   print(size,json.dumps(v,ensure_ascii=False));assert v['side']['x']>v['main']['x']+v['main']['width']-3,v
   assert v['nav']['x']>=v['side']['x']+v['side']['w']-3,v
   assert v['main']['width']>v['side']['w']*1.8,v
   await p.screenshot(path=f'/mnt/data/metstat_r87_work/desktop_fixture_{size}.png',full_page=False)
   await ctx.close()
  await b.close()
asyncio.run(main())

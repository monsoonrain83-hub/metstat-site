const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const pagePath = path.resolve(process.argv[2] || 'index.html');
if (!fs.existsSync(pagePath)) throw Error('Missing built index: '+pagePath);
(async () => {
  const browser = await chromium.launch({headless:true});
  const profiles=[
    {name:'mobile',width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:2},
    {name:'mobile-desktop-site-simulation',width:980,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1},
    {name:'desktop',width:1440,height:900,isMobile:false,hasTouch:false,deviceScaleFactor:1}
  ];
  let failed=false;
  for(const profile of profiles){
    const ctx=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.isMobile,hasTouch:profile.hasTouch,deviceScaleFactor:profile.deviceScaleFactor});
    const page=await ctx.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto('file://'+pagePath,{waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForTimeout(1200);
    const result=await page.evaluate(()=>({
      title:document.title,
      body:!!document.body,
      docWidth:document.documentElement.scrollWidth,
      innerWidth:window.innerWidth,
      focusCSS:[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.cssText&&r.cssText.includes('--msui-focus'))}catch(e){return false}}),
      navCount:document.querySelectorAll('nav, [role=navigation]').length
    }));
    console.log(profile.name,JSON.stringify({result,errors}));
    if(!result.body||!result.focusCSS||errors.length) failed=true;
    await ctx.close();
  }
  await browser.close();
  if(failed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});

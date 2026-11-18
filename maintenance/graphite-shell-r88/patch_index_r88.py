#!/usr/bin/env python3
"""r88 minimal visual-only overlay plus mobile loader note, preserving GIS and navigation logic."""
from pathlib import Path
import sys,hashlib
base=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/metstat_r87_work/public/index.html')
out=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/metstat_r88_work/public/index.html')
s=base.read_text(encoding='utf-8')
BASE='0bae22246d80a2d0c4e390166b9812624d9e100caa85c4de0fbd34a0cf5fdddc'
actual=hashlib.sha256(s.encode()).hexdigest()
if actual!=BASE:raise ValueError('r87 baseline mismatch; refusing to overwrite: '+actual)
def one(old,new,what):
 global s
 assert s.count(old)==1,(what,s.count(old))
 s=s.replace(old,new,1)
one('<link rel="stylesheet" href="assets/metstat_desktop_shell_v87.css?v=87">',
    '<link rel="stylesheet" href="assets/metstat_graphite_shell_v88.css?v=88">',
    'remove r87 fixed rail; load top nav graphite skin')
anchor='  clearInterval(e.__t); clearTimeout(e.__h); e.classList.remove("off"); e.hidden=false; document.body.classList.add("msLoading");'
new='''  /* r88: mobile is detected from the physical device, NOT the virtual desktop viewport. */
  const isPhone=(navigator.userAgentData&&navigator.userAgentData.mobile===true)||/Android|iPhone|iPod|Mobile/i.test(navigator.userAgent||"")||(navigator.maxTouchPoints>1&&Math.min(screen.width||9999,screen.height||9999)<800);
  let hint=e.querySelector("#msMobileRotateHint");
  e.classList.toggle("ms88-mobile",Boolean(isPhone));
  if(isPhone){
    if(!hint){hint=document.createElement("p");hint.id="msMobileRotateHint";hint.setAttribute("role","status");e.querySelector(".mlBox").appendChild(hint);}
    hint.textContent=document.documentElement.lang==="en"?"For a better mobile experience, rotate your phone and use the site in landscape mode.":"برای تجربه بهتر در موبایل، گوشی رو بچرخونید و در حالت افقی از سایت استفاده کنید.";
  }else if(hint){hint.remove();}
''' + anchor
one(anchor,new,'add loader hint only for mobile')
assert 'metstat_desktop_shell_v87.css?v=87' not in s
assert 'osm_settlements_v87' in s
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(s,encoding='utf-8')
print('input',actual,'output',hashlib.sha256(s.encode()).hexdigest(),'lines',s.count('\n')+1)

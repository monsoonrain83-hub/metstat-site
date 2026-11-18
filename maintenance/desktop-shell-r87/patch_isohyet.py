#!/usr/bin/env python3
"""Only layout and a saved-PNG shortcut; preserve original isohyet math and IDs."""
from pathlib import Path
import hashlib
inp=Path('/mnt/data/metstat_r86_work/station_isohyet_r86.html')
out=Path('/mnt/data/metstat_r87_work/public/online/station_isohyet_v26.html');out.parent.mkdir(parents=True,exist_ok=True)
s=inp.read_text()
def one(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b,1)
one('<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=1180, user-scalable=yes">')
one('</style><script src="../assets/map_layers.js"></script>','</style><link rel="stylesheet" href="../assets/metstat_isohyet_desktop_v87.css?v=87"><script src="../assets/map_layers.js"></script>')
# Add top save shortcut without removing or modifying the original Save or onclick.
one('</body>', '''<script id="metstat-isohyet-r87-shortcut">
(function(){'use strict';
 function start(){const source=document.getElementById('mapPosterSave'),bar=document.getElementById('mapZoomIn')?.parentElement;
  if(!source||!bar||document.getElementById('mapSaveTop'))return;
  const b=document.createElement('button');b.type='button';b.id='mapSaveTop';b.textContent='ذخیره PNG همراه عنوان، تاریخ و لوگو';
  b.disabled=source.disabled;b.onclick=()=>source.click();bar.insertBefore(b,bar.firstChild);
  new MutationObserver(()=>{b.disabled=source.disabled;}).observe(source,{attributes:true,attributeFilter:['disabled']});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
</script>
</body>''')
out.write_text(s)
print('patched',len(s),'SHA',hashlib.sha256(s.encode()).hexdigest())

from pathlib import Path
from bs4 import BeautifulSoup
import re,subprocess, tempfile,hashlib,sys
import tinycss2
r=Path('/mnt/data/metstat_r87_work');src=Path('/mnt/data/metstat_r86_work/index_r86.html').read_text();s=(r/'public/index.html').read_text()
a=BeautifulSoup(src,'html.parser');b=BeautifulSoup(s,'html.parser')
ids=lambda x:[n.get('id') for n in x.find_all(id=True) if n.get('id')]
assert ids(a)==ids(b),'Some original DOM IDs modified / reordered'
assert len(a.find_all('script'))+1==len(b.find_all('script')),'Unexpected script removal'
assert len(a.find_all('style'))==len(b.find_all('style')),'Style blocks changed'
assert len(a.select('div.wrap'))==len(b.select('div.wrap')),'Routes removed'
assert 'width=1360' in s
assert 'x.moveTo(X,Y-r*1.2)' not in s
assert 'metstat_osm_settlements_v87.js' in s
assert 'MS_GEO_LEVEL' in s
assert len(a.find_all(id='msNav'))==len(b.find_all(id='msNav'))==1
assert len(a.select('select'))==len(b.select('select'))
assert 'GEO_RK_KC=[5,30,90,190]' in s
for idx,x in enumerate(b.select('script:not([src])')):
 source=x.string or x.get_text()
 if not source.strip():continue
 t=Path(tempfile.gettempdir())/f'ms87_{idx}.js';t.write_text(source)
 c=subprocess.run(['node','--check',str(t)],capture_output=True,text=True)
 assert c.returncode==0,(idx,c.stderr[:400]);t.unlink()
css=(r/'public/assets/metstat_desktop_shell_v87.css').read_text();parsed=tinycss2.parse_stylesheet(css,skip_comments=True,skip_whitespace=True)
errs=[x for x in parsed if x.type=='error'];assert not errs,errs
for style in b.select('style'):
 data=tinycss2.parse_stylesheet(style.string or style.get_text(),skip_comments=True,skip_whitespace=True)
 if [x for x in data if x.type=='error']:
  raise AssertionError('CSS parser error in '+str(style.get('id')))
print('PASS: all original DOM IDs, selectors and page containers retained; inline JS syntax; CSS parser; desktop viewport; OSM bridge; 0 removed select controls')

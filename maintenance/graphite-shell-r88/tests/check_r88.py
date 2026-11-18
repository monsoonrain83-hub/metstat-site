import re,os,json,hashlib,subprocess,tempfile
from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2
src=Path('/mnt/data/metstat_r87_work/public/index.html').read_text()
out=Path('/mnt/data/metstat_r88_work/public/index.html').read_text()
css=Path('/mnt/data/metstat_r88_work/public/assets/metstat_graphite_shell_v88.css').read_text()
soup0=BeautifulSoup(src,'html.parser');soup=BeautifulSoup(out,'html.parser')
assert set(x.get('id') for x in soup0.find_all(id=True))==set(x.get('id') for x in soup.find_all(id=True))
assert len(soup.find_all('select'))==len(soup0.find_all('select'))
assert len(soup.find_all('script',src=True))==len(soup0.find_all('script',src=True))
assert out.count('msMobileRotateHint')>=2
assert not 'metstat_desktop_shell_v87.css?v=87' in out
assert out.count('metstat_graphite_shell_v88.css?v=88')==1
assert out.count('metstat_osm_settlements_v87.js?v=87')==1
badcss=[x for x in tinycss2.parse_stylesheet(css,skip_whitespace=True,skip_comments=True) if x.type=='error']
assert not badcss,[str(x) for x in badcss]
blocks=0
with tempfile.TemporaryDirectory() as td:
 for t in soup.find_all('script'):
  if t.get('src') or (t.get('type') not in (None,'','text/javascript','module')):continue
  data=t.string or t.get_text()
  if not data.strip():continue
  f=Path(td)/f'script_{blocks}.js';f.write_text(data)
  p=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
  assert p.returncode==0,(blocks,p.stderr[-1200:])
  blocks+=1
print(json.dumps({'html_ids':len(soup.find_all(id=True)),'selects':len(soup.find_all('select')),'inline_js_valid':blocks,'new_css_parse_errors':len(badcss),'sha256':hashlib.sha256(out.encode()).hexdigest()}))

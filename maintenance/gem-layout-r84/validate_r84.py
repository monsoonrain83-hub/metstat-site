from pathlib import Path
import sys
from bs4 import BeautifulSoup
from subprocess import run
import tempfile, hashlib, re
import tinycss2
if len(sys.argv) != 3: raise SystemExit('Usage: python validate_r84.py INPUT_INDEX.html PATCHED_INDEX.html')
base=Path(sys.argv[1]); patched=Path(sys.argv[2])
a=base.read_text('utf8');b=patched.read_text('utf8')
print('Base length',len(a),'Patched length',len(b),'difference',len(b)-len(a))
assert b.count('/* MetStat gem-display-layout-fix r84 */')==1
assert len(re.findall(r'function wxModelChips\(all\)',b))==1
assert len(re.findall(r'function nvRunSel\(m\)',b))==1
assert a.count('assets/map_layers.js')==b.count('assets/map_layers.js')
assert b.count('data:font/woff2')==a.count('data:font/woff2')
for path,text in [('original',a),('patched',b)]:
 soup=BeautifulSoup(text,'html.parser')
 sc=soup.find_all('script');inline=[s.text for s in sc if not s.get('src') and s.text.strip()]
 with tempfile.TemporaryDirectory() as tmp:
  fails=[]
  for i,src in enumerate(inline):
   f=Path(tmp)/(f'part{i}.js');f.write_text(src)
   p=run(['node','--check',str(f)],capture_output=True,text=True)
   if p.returncode:fails.append((i,p.stderr[:200]))
  print(path,'scripts',len(sc),'inline',len(inline),'node_failed',fails)
  assert not fails
 styles=[x.text for x in soup.find_all('style')]
 bad=[]
 for j,css in enumerate(styles):
  for token in tinycss2.parse_stylesheet(css,skip_comments=True,skip_whitespace=True):
   if token.type=='error':bad.append((j,token.message))
 print(path,'styles',len(styles),'CSS parse errors',bad)
 assert not bad
print('Original SHA256',hashlib.sha256(base.read_bytes()).hexdigest())
print('Patched SHA256',hashlib.sha256(patched.read_bytes()).hexdigest())

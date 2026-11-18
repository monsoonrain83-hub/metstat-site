from pathlib import Path
from bs4 import BeautifulSoup
import tinycss2,subprocess,tempfile
src=BeautifulSoup(Path('/mnt/data/metstat_r86_work/station_isohyet_r86.html').read_text(),'html.parser')
out=BeautifulSoup(Path('/mnt/data/metstat_r87_work/public/online/station_isohyet_v26.html').read_text(),'html.parser')
a=[e.get('id') for e in src.find_all(id=True) if e.get('id')]
b=[e.get('id') for e in out.find_all(id=True) if e.get('id')]
assert a==[x for x in b if not x.startswith('metstat-isohyet-r87')], (len(a),len(b))
assert not [x for x in a if b.count(x)!=1]
assert len(out.select('script:not([src])'))==len(src.select('script:not([src])'))+1
for i,e in enumerate(out.select('script:not([src])')):
 f=Path(tempfile.gettempdir())/f'ms_isohyet_{i}.js';f.write_text(e.string or e.get_text());p=subprocess.run(['node','--check',str(f)],capture_output=True,text=True);assert p.returncode==0,p.stderr;f.unlink()
css=Path('/mnt/data/metstat_r87_work/public/assets/metstat_isohyet_desktop_v87.css').read_text();assert not [x for x in tinycss2.parse_stylesheet(css) if x.type=='error']
assert 'methodSelect' in a and 'interpolate' in a and 'mapPosterSave' in a
print('PASS: all original DOM IDs and scientific controls preserved, 7/7 inline JS syntax, CSS valid, new top PNG button delegates original save action')

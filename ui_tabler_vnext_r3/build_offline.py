"""Build a no-network, single-file MetStat UI r3 preview for mobile/desktop."""
from pathlib import Path
import base64
import re
import html

ROOT=Path(__file__).resolve().parent
src=(ROOT/'index.html').read_text(encoding='utf8')
css=(ROOT/'styles.css').read_text(encoding='utf8')
webp=base64.b64encode((ROOT/'assets/homepage_atmosphere.webp').read_bytes()).decode('ascii')
css=css.replace("url('assets/homepage_atmosphere.webp')", "url('data:image/webp;base64,"+webp+"')")
assert 'assets/homepage_atmosphere.webp' not in css
src,n=re.subn(r'<link rel="stylesheet" href="styles.css">',lambda m:'<style>\n'+css+'\n</style>',src,count=1)
assert n==1
inline=[]
for name in ('route-data.js','palette-data.js','app.js'):
    src,n=re.subn(r'<script defer src="'+re.escape(name)+r'"></script>', '',src,count=1)
    assert n==1,name
    inline.append('<script>\n'+(ROOT/name).read_text(encoding='utf8').replace('</script>','<\\/script>')+'\n</script>')
# Strictly no remote network access; this is a local-only file. Embedded scripts
# need inline permission but cannot fetch remote data or open frames.
src=re.sub(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">', '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; font-src data:; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; connect-src \'none\'; object-src \'none\'; frame-src \'none\'; base-uri \'none\'; form-action \'none\'">',src,count=1)
assert '<meta http-equiv="Content-Security-Policy"' in src
src=src.replace('</body>','\n'.join(inline)+'\n</body>')
assert 'src="app.js"' not in src
assert 'url(assets/' not in src
file=ROOT/'MetStat_vNext_r3_ALL_PAGES_INTERACTIVE_OFFLINE.html'
file.write_text(src,encoding='utf8')
print('Built',file,len(src),'bytes; no external scripts or styles')
"""Build an immutable, self-contained, offline UX-only MetStat r4 review file."""
from pathlib import Path
import base64,re
R=Path(__file__).resolve().parent
html=(R/'index.html').read_text(encoding='utf8')
css=(R/'styles.css').read_text(encoding='utf8')
asset=base64.b64encode((R/'assets/homepage_atmosphere.webp').read_bytes()).decode('ascii')
css=css.replace("url('assets/homepage_atmosphere.webp')", "url('data:image/webp;base64,"+asset+"')")
assert "url('assets/homepage_atmosphere.webp')" not in css
html,n=re.subn(r'<link rel="stylesheet" href="styles.css">',lambda m:'<style>\n'+css+'\n</style>',html,count=1);assert n==1
# No phantom script/style references allowed. Fail instead of building a broken file.
assert 'r4-enhancements.css' not in html and 'r4-enhancements.js' not in html
inline=[]
for name in ['route-data.js','palette-data.js','app.js','account-r4.js','drawing-r4.js']:
 html,n=re.subn('<script defer src="'+re.escape(name)+'"></script>','',html,count=1)
 assert n==1,name
 inline.append('<script>\n'+(R/name).read_text(encoding='utf8').replace('</script>','<\\/script>')+'\n</script>')
html,n=re.subn(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">',"<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src data:; font-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'\">",html,count=1);assert n==1
html=html.replace('</body>','\n'.join(inline)+'\n</body>')
p=R/'MetStat_vNext_r4_ALL_PAGES_USER_DRAWING_INTERACTIVE_OFFLINE.html';p.write_text(html,encoding='utf8')
assert 'src="app.js"' not in html and len(html)>170000
print('OK',p,p.stat().st_size,'bytes')
"""V92: replace the two legacy auto-reload paths, preserving explicit navigation."""
from pathlib import Path
import zipfile, hashlib, json, runpy
from verify_frontend_release import inspect_zip

def sha(b): return hashlib.sha256(b).hexdigest()
BASE_INDEX='22368db76d7c67f4534f8abdf9de5f54eee1160777c56548bba1872c8de58a2c'
BASE_CORE='ee373baac9806769233f4c15a7c72887026e8b766a34f86a5e3af694be31f7a3'
NEXT_INDEX='054f9d61c2d418b66df078c3550b141416f3b6e9e01262b3b632243239cee770'
NEXT_CORE='830b402e8c88464a550e6351e906e729a56650c2c54c4d972546d7cd7c9dc5fa'
BASE_ZIP='83a8a66b059f77cfc3d962e6d7f6ae84f41832aa1718487eb19fa83c76f858d5'
OLD='if(JSON.stringify(PF.d)!==before){ const n=PF.apply(); if(n){ let go=true; try{ const g="pf.rl."+id; if(sessionStorage.getItem(g)) go=false; else sessionStorage.setItem(g,"1"); }catch(e){} if(go) location.reload(); } }'
NEW='if(JSON.stringify(PF.d)!==before){ /* Engines have already read their local settings. Apply the cached defaults at the next normal document load, not mid-session. */ toast(T("پیش‌فرض‌های حساب همگام شد؛ در ورود بعدی به سایت اعمال می‌شود.","Account defaults synced; they will take effect on the next page load.")); }'
def build(h,c):
    if sha(h)!=BASE_INDEX or sha(c)!=BASE_CORE: raise ValueError('V90 baseline mismatch')
    html=h.decode();core=c.decode()
    a=html.index('/* بررسی تازگی نسخه:'); b=html.index('</script>',a)
    if html[a:b].count('location.reload()')!=1:raise ValueError('legacy updater mismatch')
    html=html[:a]+'/* Keep build metadata; HTML revalidation and content-addressed assets handle normal navigation. No forced refresh. */\nwindow.MS_BUILD="c4ba88cd79ab";\n'+html[b:]
    if core.count(OLD)!=1:raise ValueError('account reload mismatch')
    core=core.replace(OLD,NEW,1).replace('/* ورود/خروج: بارگذاری پیش‌فرض‌ها از سرور، در صورت اختلاف با localStorage اعمال و یک‌بار صفحه را تازه می‌کند */','/* ورود/خروج: بارگذاری پیش‌فرض‌ها از سرور؛ پیش‌فرض تازه در بارگذاری عادی بعدی اعمال می‌شود. */',1)
    if 'location.reload()' in core or 'location.reload()' in html:raise ValueError('unexpected reload')
    out=core.encode();name='assets/ms_r5_perf_core_'+sha(out)[:16]+'.js'
    for key in ('setInterval(','new MutationObserver('):
        if c.count(key.encode())!=out.count(key.encode()):raise ValueError('unexpected timer/observer change')
    old='assets/ms_r5_perf_core_'+BASE_CORE[:16]+'.js'
    if html.count(old)!=1:raise ValueError('unexpected core reference')
    nh=html.replace(old,name,1).encode()
    if sha(nh)!=NEXT_INDEX or sha(out)!=NEXT_CORE:raise ValueError('local/CI mismatch')
    return nh,out,name
def pair(root,h,c,n):
    p=Path(root);(p/'assets').mkdir(parents=True,exist_ok=True)
    (p/'index.html').write_bytes(h);(p/n).write_bytes(c)
if __name__=='__main__':
    z=Path('v90-artifact/MetStat_V90_upload.zip')
    if sha(z.read_bytes())!=BASE_ZIP:raise ValueError('unexpected V90 artifact')
    h,c,n,_=inspect_zip(z)
    pair('v92-baseline',h,c,n)
    nh,nc,nn=build(h,c)
    pair('v92-candidate',nh,nc,nn)
    fetch=runpy.run_path(str(Path(__file__).with_name('build-v89-tile-raster.py')))['fetch']
    approved={BASE_INDEX:BASE_CORE,'a27298eb66145a9a8890d21c57330058876b2dd75b0b81604242b62ff9151936':'cc3b5fc40594635e03338489bd03fb205de19573938926988d1924f869f92631'}
    live=sha(fetch('/',2_000_000))
    if live not in approved:raise ValueError('unrecognized live frontend')
    d=approved[live]
    if sha(fetch('/assets/ms_r5_perf_core_'+d[:16]+'.js',6_000_000))!=d:raise ValueError('live pair mismatch')
    Path('v92-live-baseline.json').write_text(json.dumps({'index_sha256':live,'core_sha256':d}))
    Path('v92-manifest.json').write_bytes(fetch('/online/data/manifest.json',20_000_000))
    print(sha(nh),nn,sha(nc))

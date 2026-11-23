"""Apply a narrowly scoped release only to the verified live site revision."""
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
BACKUP = ROOT / 'backup'
CHECKS = json.loads((ROOT/'checksums.json').read_text())
EXTRAS = ['assets/ava_toolbox_entry.js','toolbox.html']
FILES = ['online/model_catalog.php','assets/sfc_gallery.js','assets/metstat_core_v105.js','index.html','version.json'] + EXTRAS


def prepare():
    for name, digest in CHECKS['before'].items():
        request = Request('https://wtafkik.ir/'+name+'?release_preflight=r115',headers={'Cache-Control':'no-cache'})
        with urlopen(request, timeout=120) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != digest:
            raise RuntimeError('Live site revision changed: '+name)
        dest = OUT/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(content)
        subprocess.run(['patch','--batch','--fuzz=0',str(dest),str(ROOT/(name.replace('/','_')+'.patch'))],check=True)
        if hashlib.sha256(dest.read_bytes()).hexdigest() != CHECKS['after'][name]:
            raise RuntimeError('Patched file differs: '+name)
    for name in FILES[:2] + EXTRAS:
        dest = OUT/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy(ROOT/name,dest)
    # Preserve the verified r115 patch hashes; append only an isolated toolbox script.
    index_path = OUT / 'index.html'
    index_text = index_path.read_text(encoding='utf-8')
    anchor = '<script src="assets/sfc_gallery.js?v=115.0"></script>'
    entry = '<script src="assets/ava_toolbox_entry.js?v=115.1" defer></script>'
    if index_text.count(anchor) != 1:
        raise RuntimeError('Verified index insertion point changed')
    if entry not in index_text:
        index_path.write_text(index_text.replace(anchor, anchor + chr(10) + entry, 1), encoding='utf-8')
    for name in ('assets/metstat_core_v105.js','assets/sfc_gallery.js','assets/ava_toolbox_entry.js'):
        subprocess.run(['node','--check',str(OUT/name)],check=True)
    subprocess.run(['php','-l',str(OUT/'online/model_catalog.php')],check=True)


def deploy():
    # Existing live files are compared again through FTPS before the first write.
    ftp = ftplib.FTP_TLS(timeout=120)
    ftp.connect(os.environ['FTP_SERVER'])
    ftp.login(os.environ['FTP_USERNAME'],os.environ['FTP_PASSWORD'])
    ftp.prot_p()
    ftp.cwd(os.environ.get('FTP_DIR') or '/')
    original = {}
    try:
        for name in FILES:
            data = io.BytesIO()
            try:
                ftp.retrbinary('RETR '+name,data.write)
                original[name] = data.getvalue()
            except ftplib.error_perm as error:
                if name in CHECKS['before'] or not str(error).startswith('550'):
                    raise
                original[name] = None
            if name in CHECKS['before'] and hashlib.sha256(original[name]).hexdigest() != CHECKS['before'][name]:
                raise RuntimeError('FTPS live revision differs: '+name)
            if original[name] is not None:
                dest = BACKUP/name
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(original[name])
        written = []
        try:
            for name in FILES:
                temporary = name + '.r115.tmp'
                ftp.storbinary('STOR '+temporary,io.BytesIO((OUT/name).read_bytes()))
                check = io.BytesIO()
                ftp.retrbinary('RETR '+temporary,check.write)
                if check.getvalue() != (OUT/name).read_bytes():
                    raise RuntimeError('Upload verification failed: '+name)
                written.append(name)
                ftp.rename(temporary,name)
                print('Verified upload',name,flush=True)
        except Exception:
            for name in reversed(written):
                if original[name] is not None:
                    ftp.storbinary('STOR '+name,io.BytesIO(original[name]))
                else:
                    try: ftp.delete(name)
                    except ftplib.error_perm: pass
            raise
    finally:
        ftp.close()


if __name__ == '__main__':
    if '--deploy' in sys.argv:
        deploy()
    else:
        prepare()

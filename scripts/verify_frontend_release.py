"""Verify a narrow core-only frontend release against its exact approved base.

No archive extraction, network requests, deployment, or mutation. Full releases
that intentionally alter HTML need a different, explicitly approved contract.
"""
import hashlib
import re
import stat
import sys
import zipfile
from pathlib import Path

CORE = re.compile(r'assets/ms_r5_perf_core_([a-f0-9]{16})\.js\Z')
MAX_CORE = 8_000_000
MAX_INDEX = 2_000_000

def digest(b):
    return hashlib.sha256(b).hexdigest()

def inspect_zip(path):
    with zipfile.ZipFile(path) as z:
        entries=z.infolist()
        if len(entries)!=2 or len({x.filename for x in entries})!=2:
            raise ValueError('expected exactly two distinct files')
        names={x.filename for x in entries}
        cores=[n for n in names if CORE.fullmatch(n)]
        if len(cores)!=1 or names!={'index.html',cores[0]}:
            raise ValueError('unexpected deployment path')
        name=cores[0]
        for x in entries:
            mode=(x.external_attr>>16)&0xFFFF
            if x.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG) or x.flag_bits&1:
                raise ValueError('nonregular or encrypted entry')
            if not 0<x.file_size<=(MAX_INDEX if x.filename=='index.html' else MAX_CORE):
                raise ValueError('invalid deployment file size')
        index=z.read('index.html');core=z.read(name)
        if digest(core)[:16]!=CORE.fullmatch(name).group(1):
            raise ValueError('core filename/content hash mismatch')
        ref=('<script src="/'+name+'"></script>').encode()
        if index.count(ref)!=1 or len(re.findall(rb'/assets/ms_r5_perf_core_[a-f0-9]+\.js',index))!=1:
            raise ValueError('missing or duplicate core reference')
        return index,core,name,ref

def verify(path,base_index,base_core,base_name):
    if not CORE.fullmatch(base_name) or digest(base_core)[:16]!=CORE.fullmatch(base_name).group(1):
        raise ValueError('invalid baseline core hash')
    index,core,name,ref=inspect_zip(path)
    old_ref=('<script src="/'+base_name+'"></script>').encode()
    if base_index.count(old_ref)!=1 or index!=base_index.replace(old_ref,ref,1):
        raise ValueError('unexpected HTML changes outside approved reference')
    if name==base_name or core==base_core:
        raise ValueError('no core change')
    return {'baseline_index_sha256':digest(base_index),'baseline_core_sha256':digest(base_core),'index_sha256':digest(index),'core_sha256':digest(core),'core':name,'zip_sha256':digest(Path(path).read_bytes())}

if __name__=='__main__':
    import json
    base=Path(sys.argv[2]);cores=list((base/'assets').glob('ms_r5_perf_core_*.js'))
    if len(cores)!=1: raise SystemExit('expected one baseline core')
    try: print(json.dumps(verify(sys.argv[1],(base/'index.html').read_bytes(),cores[0].read_bytes(),cores[0].relative_to(base).as_posix()),indent=2))
    except (ValueError, OSError, zipfile.BadZipFile) as e: raise SystemExit(str(e))

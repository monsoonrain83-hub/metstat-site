#!/usr/bin/env python3
"""Build a local indexed gazetteer from sajaddp/list-of-cities-in-Iran CSV ZIP.
Not a sensor database: names/province/county only; source has no lat/lon for villages.
"""
import argparse,csv,io,sqlite3,zipfile,re,os

def norm(s):
 s=str(s or '').strip().translate(str.maketrans({'ي':'ی','ى':'ی','ك':'ک','أ':'ا','إ':'ا','ؤ':'و','ئ':'ی','آ':'ا','ة':'ه','ۀ':'ه'}))
 s=re.sub('[\u064b-\u065f\u0670\u06d6-\u06ed]', '', s)
 s=re.sub(r'[\u200c\u200d_#./،,؛:()\[\]{}-]', ' ', s)
 return ' '.join(s.lower().split())

def rows(z,kind):
  n=next((n for n in z.namelist() if n.endswith('/dist/csv/'+kind+'.csv')),None)
  if not n: raise ValueError('Missing CSV '+kind)
  with z.open(n) as f:yield from csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig'))

def build(src,dst):
 with zipfile.ZipFile(src) as z:
  prov={r['id']:r['name'] for r in rows(z,'provinces')}
  counties={r['id']:r['name'] for r in rows(z,'counties')}
  if os.path.exists(dst):os.remove(dst)
  con=sqlite3.connect(dst)
  con.executescript('''
  PRAGMA journal_mode=DELETE;
  CREATE TABLE places(id TEXT PRIMARY KEY, name TEXT NOT NULL, normalized TEXT NOT NULL, compact TEXT NOT NULL,
  province TEXT NOT NULL,county TEXT NOT NULL,province_id TEXT NOT NULL, county_id TEXT NOT NULL,type TEXT NOT NULL);
  CREATE INDEX ix_names ON places(normalized,province,county);
  CREATE INDEX ix_compact ON places(compact,province);
  CREATE INDEX ix_admin ON places(province,county);
  ''')
  count=0
  for kind in ('cities','villages'):
    batch=[]
    for r in rows(z,kind):
      n=r.get('name','').strip(); p=prov.get(r.get('province_id','')); c=counties.get(r.get('county_id',''))
      if not n or not p or not c:continue
      nm=norm(n)
      batch.append((str(r['id']),n,nm,nm.replace(' ',''),p,c,r['province_id'],r['county_id'],kind))
      if len(batch)>2000:
        con.executemany('INSERT OR IGNORE INTO places VALUES (?,?,?,?,?,?,?,?,?)',batch);count+=len(batch);batch.clear()
    if batch:con.executemany('INSERT OR IGNORE INTO places VALUES (?,?,?,?,?,?,?,?,?)',batch);count+=len(batch)
  con.commit();print('Inserted:',con.execute('select count(*) from places').fetchone()[0])
  for name in ('امامزاده اسحاق','شیاده بالا','چابکسر'):
    print(name,con.execute('select name,province,county from places where normalized=?',(norm(name),)).fetchall()[:5])
  con.close()
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('zip');ap.add_argument('output');a=ap.parse_args();build(a.zip,a.output)

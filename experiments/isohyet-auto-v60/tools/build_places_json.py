#!/usr/bin/env python3
"""Build province-sharded O(1) name-to-county index from user-supplied Iranian place archive.
GPL-3.0 source; distribute matching license text and provenance with generated data.
"""
import csv,io,json,os,re,sys,zipfile
from collections import defaultdict

def norm(s):
 s=str(s or '').strip().translate(str.maketrans({'ي':'ی','ى':'ی','ك':'ک','أ':'ا','إ':'ا','ؤ':'و','ئ':'ی','آ':'ا','ة':'ه','ۀ':'ه'}))
 s=re.sub(r'[\u064b-\u065f\u0670\u06d6-\u06ed]', '', s)
 s=re.sub(r'[\u200c\u200d_#./،,؛:()\[\]{}-]', ' ', s)
 return ' '.join(s.lower().split())
def read(z,typ):
 fn=next(x for x in z.namelist() if x.endswith('/dist/csv/'+typ+'.csv'))
 with z.open(fn) as f: yield from csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig'))
def main(src,out):
 os.makedirs(out,exist_ok=True)
 with zipfile.ZipFile(src) as z:
  prov={r['id']:r['name'] for r in read(z,'provinces')};cnt={r['id']:r['name'] for r in read(z,'counties')}
  json.dump(prov,open(os.path.join(out,'provinces.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
  grouped=defaultdict(lambda:defaultdict(list));total=0
  for kind in ('cities','villages'):
   for r in read(z,kind):
    p=r.get('province_id','');c=r.get('county_id','');name=r.get('name','').strip()
    if p not in prov or c not in cnt or not name:continue
    row={'name':name,'county':cnt[c],'county_id':c,'type':kind,'id':r['id']}
    grouped[p][norm(name)].append(row);total+=1
  for p,names in grouped.items():
   doc={'province':prov[p],'province_id':p,'names':names}
   with open(os.path.join(out,'p_'+p+'.json'),'w',encoding='utf-8') as f:json.dump(doc,f,ensure_ascii=False,separators=(',',':'))
  print('Indexed',total,'places in',len(grouped),'provinces')
if __name__=='__main__':main(*sys.argv[1:])

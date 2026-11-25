"""Rebuild narrow converter path migration from the exact verified R5 index."""
from pathlib import Path
import hashlib, json, re
index=Path("r5-candidate/index.html")
s=index.read_text()
assert hashlib.sha256(s.encode()).hexdigest()=="4426f3190fffd9d506cd7a6350507603c55ce88df07e009d6a7f8cd3d7ff44b3"
def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)
m=re.search(r'const paths=Object\.freeze\((\{[^\n]+\})\);',s)
paths=json.loads(m.group(1)); aliases={}
for k,slug in {'convert-unit':'unit','convert-weather':'weather-file','convert-media':'media','convert-document':'document'}.items():
    aliases[paths[k]]=k
    paths[k]='/meteorological-toolbox/converter/'+slug
assert len(paths)==len(set(paths.values())) and len(aliases)==4
s=once(s,m.group(0),'const paths=Object.freeze('+json.dumps(paths,separators=(',',':'))+');\n const aliases=Object.freeze('+json.dumps(aliases,separators=(',',':'))+');')
s=once(s,"return Object.keys(paths).find(k=>paths[k]===h||paths[k]===p)||'';}","return Object.keys(paths).find(k=>paths[k]===h||paths[k]===p)||aliases[h]||aliases[p]||'';}")
s=once(s,'window.MS_R5_CUSTOM_ROUTE={paths,current,active:!!current()};','window.MS_R5_CUSTOM_ROUTE={paths,aliases,current,active:!!current()};')
a="const item=NAV.flatMap(g=>g[3]).find(x=>x[1]===dest);if(item)navigate(dest,item[0],true);"
b="""const item=NAV.flatMap(g=>g[3]).find(x=>x[1]===dest);if(item){
      const r=window.MS_R5_CUSTOM_ROUTE,p=location.pathname.replace(/\\/+$/,''),h=location.hash.replace(/^#\\/?/,'/').replace(/\\/+$/,'');
      if(r.aliases[p]===dest||r.aliases[h]===dest){const target=r.aliases[h]===dest?'/index.html'+location.search+'#'+r.paths[dest]:r.paths[dest]+location.search;history.replaceState(history.state,'',target);}
      navigate(dest,item[0],true);
     }"""
s=once(s,a,b)
index.write_text(s)
Path("r5-converter-routes.json").write_text(json.dumps({"canonical":{k:paths[k] for k in aliases.values()},"aliases":aliases},indent=2)+"\n")
print("Four canonical converter routes; legacy aliases preserved; no engine changed.")

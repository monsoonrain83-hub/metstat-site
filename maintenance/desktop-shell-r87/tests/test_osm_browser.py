import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 root=Path('/mnt/data/metstat_r87_work/public');d=json.loads((root/'data/osm_settlements_v87.json').read_text())
 async with async_playwright() as pw:
  b=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  ctx=await b.new_context(viewport={'width':1366,'height':820});p=await ctx.new_page()
  await p.set_content('<!doctype html><html lang=fa dir=rtl><body><canvas id=c width=1200 height=720></canvas></body></html>')
  await p.add_script_tag(content=(root/'assets/metstat_osm_settlements_v87.js').read_text())
  res=await p.evaluate('''(nodes)=>{ MetStatOSM.indexNodes(nodes);let a=MetStatOSM.query(29.5,30.5,51.5,53.0);let cv=document.getElementById('c');let x=cv.getContext('2d');let n=MetStatOSM.drawNwp(x,1200,720,600,51.5,30.5,1,[],[]);return{ready:MetStatOSM.state.ready,full:MetStatOSM.state.nodes.length,visible:a.length,drawn:n,example:a.slice(0,3).map(p=>p[2])}}''',d['nodes'])
  assert res['ready'] and res['full']==55065 and res['visible']>100 and res['drawn']>0,res
  print('OSM TEST:',res)
  await p.screenshot(path='/mnt/data/metstat_r87_work/osm_canvas_test.png')
  await b.close()
asyncio.run(main())

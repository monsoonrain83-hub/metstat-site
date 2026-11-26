// Real browser HTTP cache regression: separate loopback context, no route interception.
const {chromium}=require('playwright');
const http=require('node:http'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root='v82-candidate/assets';const core=fs.readFileSync(root+'/'+fs.readdirSync(root).find(x=>x.startsWith('ms_r5_perf_core_')),'utf8');
const helper=core.slice(core.indexOf('async function ms82FetchManifest('),core.indexOf('\nasync function onLoadManifest(){'));
const manifest=JSON.parse(fs.readFileSync('public-manifest.json','utf8'));
let body=Buffer.from(JSON.stringify(manifest)),fault=false;const hits=[];
const server=http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');if(u.pathname==='/'){res.setHeader('Content-Type','text/html');res.end('<html><body>HTTP cache regression</body></html>');return;}
 if(u.pathname!=='/online/data/manifest.json'){res.writeHead(404);res.end();return;}
 const etag='"'+crypto.createHash('sha256').update(body).digest('hex')+'"';
 const status=fault&&!u.search?503:req.headers['if-none-match']===etag?304:200;
 hits.push({status,query:!!u.search,bytes:status===200?body.length:0,conditional:!!req.headers['if-none-match']});
 res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'public, no-cache',ETag:etag});
 res.end(status===200?body:undefined);
});
(async()=>{
 let browser;try{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));browser=await chromium.launch();const page=await browser.newPage();
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  await page.evaluate(code=>(0,eval)(code+'\nwindow.ms82FetchManifest=ms82FetchManifest;'),helper);
  const get=()=>page.evaluate(async()=>{const m=await ms82FetchManifest('/online/');return [m.updated,m.items.length,m.items_prev?.length||0,Object.keys(m.models).length]});
  const a=await get(),b=await get();assert.deepEqual(a,b);assert.equal(hits.at(-1).status,304);
  manifest.updated='v82-test-updated';body=Buffer.from(JSON.stringify(manifest));const c=await get();assert.equal(c[0],manifest.updated);assert.deepEqual(c.slice(1),a.slice(1));assert.equal(hits.at(-1).status,200);
  fault=true;assert.deepEqual(await get(),c);assert.equal(hits.at(-2).status,503);assert.equal(hits.at(-1).status,200);assert(hits.at(-1).query);
  console.log(JSON.stringify({rows:a.slice(1),hits},null,2));
  fs.writeFileSync('v82-cache-report.json',JSON.stringify({rows:a.slice(1),hits},null,2));
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
const port=3220;
const server=spawn(process.execPath,['node_modules/next/dist/bin/next','start','-p',String(port),'-H','127.0.0.1'],{stdio:'pipe'});
let output='';
server.stderr.on('data',chunk=>{output+=String(chunk).slice(0,2000);});
const base=`http://127.0.0.1:${port}`;
try {
 let response;
 for(let attempt=0;attempt<40;attempt++) {
  try {response=await fetch(base+'/api/catalog?q=Pikachu');break;}
  catch {if(server.exitCode!==null)throw new Error(`Server exited: ${output}`);await new Promise(r=>setTimeout(r,250));}
 }
 assert.ok(response,`Server did not start: ${output}`);
 assert.equal(response.status,200);
 const catalog=await response.json();
 assert.ok(catalog.cards.some(c=>c.name==='Pikachu'));
 assert.ok(catalog.cards.length<=24);
 for(const path of ['/','/catalogo','/atlas','/analise','/shop','/colecao','/comunidade','/planos','/login','/legal']) {
  const page=await fetch(base+path);assert.equal(page.status,200,path);const html=await page.text();assert.match(html,/CardCraftAI/);assert.doesNotMatch(html,/href="https:\/\/cardcraftai-test\.streamlit\.app/);
 }
 for(const route of ['/api/me','/api/collection','/api/community']) {
  const r=await fetch(base+route);assert.ok([401,503].includes(r.status),route);assert.match(r.headers.get('cache-control'),/no-store/);
 }
 for(const route of ['/api/collection','/api/community','/api/atlas','/api/me','/api/auth/logout']) {
  const r=await fetch(base+route,{method:'POST',headers:{origin:'https://wrong-origin.invalid','Content-Type':'application/json'},body:'{}'});assert.equal(r.status,403,route);
 }
 const empty=await (await fetch(base+'/api/catalog?q=a')).json();assert.equal(empty.cards.length,0);
 const missing=await fetch(base+'/this-page-does-not-exist');assert.equal(missing.status,404);
 console.log('PASS: 10 pages, catalog, private-route gate, CSRF gate, cache headers, empty search and 404. No authenticated or AI test implied.');
} finally {server.kill('SIGTERM');}

import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {setup,close,agent,call,model,load} from './fixture.mjs';
import {adaptDailyPresets} from '../runtime/daily-presets.mjs';

const readonly=new Set(['suite_status','suite_search','suite_memory_recall','suite_memory_get','suite_extract']);
test('RC.2 first managed child request advertises only the governed readonly tools',{timeout:30000},async()=>{
 const f=await setup();const observations=[];try{
  const a=await agent(f);f.ctx.tools.register({name:'synthetic_mutate',description:'Synthetic mutation',parameters:{type:'object'},output:{schema:{type:'object'},render:()=>[]},execute(){throw Error('must not execute');}});
  f.behavior=options=>{const child=f.ctx.agents.get(options.sessionId);if(child?.session.header.origin==='subagent')observations.push((options.tools??[]).map(t=>t.name));};
  const result=await call(f,a,'delegate',{tasks:[{label:'readonly',prompt:'Read available evidence'}]});
  assert.equal(result.runs[0].status,'completed');assert(observations.length>0);
  assert(observations.every(names=>names.every(n=>readonly.has(n))),JSON.stringify(observations));
 }finally{await close(f);}
});

test('RC.2 official Flash route remains governed by the existing ledger',{timeout:30000},async()=>{
 const f=await setup();try{
  await model(f,{model:'deepseek-flash'});
  const ledger=JSON.parse(await readFile(f.budgetPath));assert.equal(ledger.initialSpent,1);assert.equal(ledger.entries.length,1);assert.equal(ledger.entries[0].status,'settled');
  const bytes=await readFile(f.budgetPath);await assert.rejects(model(f,{model:'arbitrary-unapproved-model'}));assert.deepEqual(await readFile(f.budgetPath),bytes);assert.equal(f.requests.length,1);
 }finally{await close(f);}
});

async function nativeRows(){const {loadOverlayPatches}=await load('@deepseek-ai/dsh-app-boot');return ['standard','cordis','minimal','ptc'].map(id=>loadOverlayPatches('dsh',join(process.env.SEP_OFFICIAL_HARNESS,'node_modules/@deepseek-ai/dsh-web-app/presets',id+'.patch.yml'))[0].insert[0]);}
test('RC.2 all four actual presets retain compact commands while inheriting the governed engine',async()=>{
 const rows=await nativeRows(),before=structuredClone(rows),adapted=adaptDailyPresets(rows);assert.deepEqual(rows,before);assert.equal(adapted.length,4);
 for(const row of adapted){const group=row.config.plugins.find(p=>p.id==='compaction');assert.equal(group.isolate.compaction,undefined);assert.equal(group.config.find(p=>p.id==='compaction-basic').disabled,true);assert(group.config.some(p=>p.id==='command-compact'));}
});
test('RC.2 unknown preset composition is refused without changing its input',async()=>{
 for(const mutate of [r=>r[2].config.plugins.find(p=>p.id==='compaction').isolate.foreign=true,r=>r[0].config.plugins.find(p=>p.id==='compaction').config.push({id:'compaction-basic',name:'foreign'}),r=>r[2].config.plugins=r[2].config.plugins.filter(p=>p.id!=='compaction')]){
  const rows=await nativeRows();mutate(rows);const bytes=JSON.stringify(rows);assert.throws(()=>adaptDailyPresets(rows),{code:'SEP_DAILY_PRESET_UNSUPPORTED'});assert.equal(JSON.stringify(rows),bytes);
 }
});

async function server(handler){const s=createServer(handler);await new Promise((resolve,reject)=>{s.once('error',reject);s.listen(0,'127.0.0.1',resolve);});return {origin:'http://127.0.0.1:'+s.address().port,close:()=>new Promise(resolve=>{s.closeAllConnections();s.close(resolve);})};}
async function receive(req){let body='';for await(const bytes of req){body+=bytes;assert(body.length<4096);}return JSON.parse(body);}
test('RC.2 new Search and Fetch providers operate in the real SEP host without auxiliary model requests',{timeout:30000},async()=>{
 const f=await setup();const seen=[];const endpoint=await server(async(req,res)=>{try{seen.push({url:req.url,body:await receive(req)});res.setHeader('content-type','application/json');res.end(JSON.stringify(req.url.endsWith('/search')?{results:[{url:'https://example.test/entry',title:'Synthetic source',snippet:'bounded excerpt',date:null}]}:{title:'Synthetic page',content:'# Body'}));}catch{res.writeHead(400).end();}});
 try{
  await f.ctx.plugin((await load('@deepseek-ai/dsh-web')).default,{searchProvider:'deepseek-search-api',fetchProvider:'deepseek-fetch-api'});
  const fiber=f.ctx.plugin(await load('@deepseek-ai/dsh-web-deepseek-api'),{apiKey:'synthetic-loopback-only',baseURL:endpoint.origin+'/v1/tools',sendOriginalQuestion:false});await fiber;
  const result=await f.ctx.web.search({query:'synthetic query',maxResults:2});assert.equal(result.sources[0].url,'https://example.test/entry');
  const fetched=await f.ctx.web.fetch({url:'https://example.test/entry'});assert.equal(fetched.body.content,'# Body');
  assert.deepEqual(seen,[{url:'/v1/tools/search',body:{query:'synthetic query',count:2,need_content:false}},{url:'/v1/tools/fetch',body:{url:'https://example.test/entry'}}]);
  assert.equal(f.requests.length,0);assert.equal(JSON.parse(await readFile(f.budgetPath)).entries.length,0);
  await fiber.dispose();await assert.rejects(f.ctx.web.search({query:'synthetic query'}));
 }finally{await endpoint.close();await close(f);}
});
test('RC.2 Search provider refuses redirects before a different endpoint is contacted',{timeout:10000},async()=>{
 let targetCalls=0;const target=await server((req,res)=>{targetCalls++;req.resume();res.end('{}');});const redirect=await server((req,res)=>{req.resume();res.writeHead(307,{location:target.origin+'/collect'}).end();});
 try{const {DeepSeekSearchApiProvider}=await load('@deepseek-ai/dsh-web-deepseek-api');const provider=new DeepSeekSearchApiProvider(()=>({apiKey:'synthetic-loopback-only',baseURL:redirect.origin,count:2}));await assert.rejects(provider.search({query:'synthetic query'}),e=>e.code==='WEB_PROVIDER_ERROR');assert.equal(targetCalls,0);}finally{await redirect.close();await target.close();}
});

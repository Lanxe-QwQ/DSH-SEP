import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {setup,close,agent,call,say,owned,load} from '../../rc2-adaptation/tests/fixture.mjs';
import {execution,hash,day} from './fixture.mjs';
async function realFixture(){
 const f=await setup({mountRoot:false});f.clock=Date.parse('2026-01-02T00:00:00.000Z');
 const {createLayeredMemory}=await owned('host/layered-memory/index.js'),{bindStorage}=await owned('modules/system-enhancement-package/src/p2/storage.js');
 f.project={key:'real-synthetic',root:f.dirs.project,userProfile:'real-shared'},f.scope={projects:[f.project]};
 f.openLayers=async()=>{f.layers=await f.storage.withAccess(()=>createLayeredMemory({facility:f.storage,scope:f.scope,legacy:{read:()=>({memories:[],index:null})},now:()=>f.clock}));};f.reopen=async()=>{f.control=await f.openControl({storageRoot:f.dirs.memory});f.storage=await bindStorage({facility:f.ctx.storageDomain,storageRoot:f.dirs.memory,control:f.control});await f.openLayers();};await f.reopen();
 f.finish=async()=>{try{await f.layers?.close();await f.control?.close();}finally{await close(f);}};
 let n=0;f.save=async(text,key='slot',extra={})=>f.layers.tools.save(f.project,{text,category:'temporary',semanticKey:key,status:'confirmed',eventId:'save-'+(++n),reason:'synthetic',...extra},execution(text,'direct-'+n));
 return f;
}
test('official Loader tools confirm a survivor after P2-governed withdrawal',async()=>{const f=await setup();try{const a=await agent(f);say(a,'项目交付 PDF');const old=await call(f,a,'memory_save',{text:'项目交付 PDF',category:'project',semanticKey:'format',status:'confirmed',eventId:'old',reason:'synthetic'});say(a,'项目交付 Markdown');const pending=await call(f,a,'memory_save',{text:'项目交付 Markdown',category:'project',semanticKey:'format',status:'confirmed',eventId:'candidate',reason:'synthetic'});say(a,'忘记旧的 PDF 交付');await call(f,a,'memory_revoke',{id:old.record.id,expectedRevision:old.record.revision,eventId:'withdraw',reason:'direct'});const current=(await call(f,a,'memory_get',{id:pending.record.id})).record;say(a,'确认采用 Markdown 并更正交付');const out=await call(f,a,'memory_revise',{id:current.id,expectedRevision:current.revision,eventId:'confirm',reason:'direct',text:current.text,status:'confirmed'});assert.equal(out.record.status,'confirmed');assert((await f.ctx.sepStorageControl.checkpoint()).deletions.some(m=>m.id===old.record.id));assert.equal(f.requests.length,0);}finally{await close(f);}});
test('official Loader recall uses current tokenizer for ordinary and on-demand archive search',async()=>{const f=await setup();try{const a=await agent(f);say(a,'买了苹果。今天吃香蕉');const out=await call(f,a,'memory_save',{text:'买了苹果。今天吃香蕉',category:'project',semanticKey:'fruit',status:'confirmed',eventId:'fruit',reason:'synthetic'});let price;for(let i=0;i<19;i++){const text='今天的苹果价格已经更新，条目 '+i;say(a,text);price=await call(f,a,'memory_save',{text,category:'project',semanticKey:'price-'+i,status:'confirmed',eventId:'price-'+i,reason:'synthetic'});}assert((await call(f,a,'memory_recall',{query:'苹果今天价格'})).records[0].text.startsWith('今天的苹果价格'));
 for(const r of [out.record,price.record]){say(a,'归档这条旧记忆');await call(f,a,'memory_archive',{id:r.id,expectedRevision:r.revision,eventId:'archive-'+r.id,reason:'synthetic'});}say(a,'请查找历史归档中的苹果今天价格');assert((await call(f,a,'memory_archive_search',{query:'苹果今天价格'})).records[0].text.startsWith('今天的苹果价格'));assert.equal(f.requests.length,0);}finally{await close(f);}});
for(let round=1;round<=3;round++)test('real JSON/P2 combined lifecycle round '+round,async()=>{const f=await realFixture();try{
 const first=(await f.save('临时安排 PDF')).record,second=(await f.save('临时安排 Markdown')).record;
 await f.layers.tools.archive(f.project,{id:first.id,expectedRevision:first.revision,eventId:'archive',reason:'synthetic'},execution('归档旧临时安排','archive-source'));
 const current=f.layers.read(f.project).find(r=>r.id===second.id);const out=await f.layers.tools.revise(f.project,{id:current.id,expectedRevision:current.revision,text:current.text,status:'confirmed',eventId:'confirm',reason:'synthetic'},execution('确认采用并更正 Markdown','confirm-source'));assert.equal(out.record.status,'confirmed');
 f.clock+=31*day;for(let n=0;n<3;n++)await f.layers.observeUserQuery(f.project,'Markdown 的安排是什么？');assert.equal(f.layers.select(f.project,'Markdown').records.length,0);
 const maintained=await f.layers.maintain(f.project);assert(maintained.changes.some(r=>r.id===second.id));assert.equal(f.layers.read(f.project).length,0);
 await f.layers.close();await f.control.close();await f.reopen();assert.equal(f.layers.read(f.project).length,0);
 const meta=JSON.parse(await readFile(join(f.dirs.memory,'dsh_four_layer_memory_v1.json')));assert(Object.values(meta.tables.active.catalog.archives).some(m=>m.recordId===second.id));
 const cancellation=new AbortController();cancellation.abort();await assert.rejects(f.layers.tools.save(f.project,{text:'不得保存',eventId:'cancel',reason:'synthetic'},execution('不得保存','cancel',cancellation.signal)));
 assert.equal(f.layers.read(f.project).length,0);
 const seed=(await f.save('临时存量','quota.seed')).record;await f.layers.close();
 const {z}=await load('zod'),domain=await f.storage.withAccess(()=>f.storage.open({name:'dsh_four_layer_memory_v1',version:1,tables:{active:{valueSchema:z.json()}}}));
 // Fixture setup only: a single governed bulk write seeds 500 valid synthetic
 // rows. The capacity operation itself still uses the actual production API.
 await f.storage.withAccess(async()=>{const table=domain.table('active'),state=table.get('catalog'),o=state.owners[seed.owner],raw=o.records.find(r=>r.id===seed.id);o.records=Array.from({length:500},(_,i)=>({...structuredClone(raw),id:i===0?raw.id:'bulk-'+round+'-'+i,semanticKey:i===0?raw.semanticKey:'bulk.slot.'+i,text:i===0?raw.text:'临时存量 '+i,pinned:i!==0}));await table.put('catalog',state);});await domain.close();await f.openLayers();assert.equal(f.layers.read(f.project).length,500);
 const duplicate=await f.save(seed.text,seed.semanticKey);assert.equal(duplicate.status,'deduplicated');assert.equal(f.layers.read(f.project).length,500);f.clock+=31*day;
 const admitted=await f.save('容量回收后新增','new.quota.slot');assert.equal(admitted.status,'saved');assert(f.layers.read(f.project).length<=500);assert(!f.layers.read(f.project).some(r=>r.id===seed.id));
 const cp=await f.control.checkpoint();assert.equal(cp.pending.length,0);assert(cp.businessSeq>0);assert.equal(f.requests.length,0);
 }finally{await f.finish();}});

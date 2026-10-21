import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdtemp,mkdir,writeFile,readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {load as owned,execution,day} from './fixture.mjs';
const require=createRequire(join(resolve(process.env.SEP_OFFICIAL_HARNESS),'package.json'));
const native=name=>import(pathToFileURL(require.resolve(name)));
async function setup(){
 const base=await mkdtemp(join(resolve(process.env.SEP_BUNDLE_TEST_ROOT),'real-memory-')),memory=join(base,'memory');await mkdir(memory);
 const conf=join(base,'cordis.yml');await writeFile(conf,'[]\n');const {boot}=await native('@deepseek-ai/dsh-app-boot');
 const ctx=await boot('dsh',conf,[],async ctx=>{for(const name of ['@deepseek-ai/dsh-storage','@deepseek-ai/dsh-storage-json','@deepseek-ai/dsh-storage-domain']){const m=await native(name);await ctx.plugin(m.default??m,name.endsWith('-json')?{root:memory}:name.endsWith('-domain')?{backend:'json'}:{});}});
 const {openControl}=await owned('modules/system-enhancement-package/src/p2/control.js'),{bindStorage}=await owned('modules/system-enhancement-package/src/p2/storage.js'),{createLayeredMemory}=await owned('host/layered-memory/index.js');
 const project={key:'portable-synthetic',root:base,userProfile:'portable-shared'},scope={projects:[project]};let clock=Date.parse('2026-01-02T00:00:00.000Z'),control,storage,layers;
 const open=async initialize=>{control=await openControl({storageRoot:memory,initialize});storage=await bindStorage({facility:ctx.storageDomain,storageRoot:memory,control});layers=await storage.withAccess(()=>createLayeredMemory({facility:storage,scope,legacy:{read:()=>({memories:[],index:null})},now:()=>clock}));};await open(true);
 let n=0;return {base,memory,project,ctx,get layers(){return layers;},get control(){return control;},advance:days=>{clock+=days*day;},async save(text,key='slot',extra={}){const id='direct-'+(++n);return layers.tools.save(project,{text,semanticKey:key,category:'temporary',status:'confirmed',eventId:id,reason:'synthetic',...extra},execution(text,id));},async reopen(){await layers.close();await control.close();await open(false);},async close(){try{await layers.close();await control.close();}finally{await ctx.fiber.dispose();}}};
}
for(let round=1;round<=3;round++)test('native storage/P2 memory repair round '+round,async()=>{const f=await setup();try{
 const a=(await f.save('临时 PDF 格式')).record,b=(await f.save('临时 Markdown 格式')).record;
 await f.layers.tools.revoke(f.project,{id:a.id,expectedRevision:a.revision,eventId:'revoke',reason:'direct'},execution('忘记旧 PDF 格式','remove-source'));
 const current=f.layers.read(f.project).find(r=>r.id===b.id);assert(!current.conflictsWith?.includes(a.id));assert(current.revision>b.revision);
 const args={id:b.id,expectedRevision:current.revision,text:b.text,status:'confirmed',eventId:'confirm',reason:'direct'};await f.layers.tools.revise(f.project,args,execution('确认采用并更正为 Markdown','confirm-source'));
 f.advance(31);await f.layers.observeUserQuery(f.project,'Markdown是什么？');assert.equal(f.layers.select(f.project,'Markdown').records.length,0);assert.equal(f.layers.readForRecall(f.project).length,0);
 await f.layers.maintain(f.project);await f.reopen();assert.equal(f.layers.read(f.project).length,0);const cp=await f.control.checkpoint();assert(cp.deletions.some(m=>m.id===a.id));assert.equal(cp.pending.length,0);assert(cp.businessSeq>0);
 const value=JSON.parse(await readFile(join(f.memory,'dsh_four_layer_memory_v1.json')));assert(Object.values(value.tables.active.catalog.archives).some(m=>m.recordId===b.id));
 const ac=new AbortController();ac.abort();await assert.rejects(f.layers.tools.save(f.project,{text:'取消',eventId:'cancel',reason:'direct'},execution('取消','cancel-source',ac.signal)));assert.equal(f.layers.read(f.project).length,0);
 const saved=(await f.save('买了苹果。今天吃香蕉','fruit',{category:'project'})).record;const {tokenizeHybridSegmented}=await owned('modules/system-enhancement-package/src/vendor/bm25.js');assert(!tokenizeHybridSegmented(saved.text).includes('果今'));
 }finally{await f.close();}});

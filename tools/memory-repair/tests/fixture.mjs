import {createHash} from 'node:crypto';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=resolve(process.env.SEP_MEMORY_SOURCE??process.cwd());
const bundle=resolve(process.env.SEP_MEMORY_BUNDLE??join(root,'bundle'));
export const load=path=>import(pathToFileURL(join(bundle,path)));
export const hash=value=>createHash('sha256').update(value).digest('hex');
export const day=86400000;
export function execution(text,id='message',signal=new AbortController().signal){
 const message={id,role:'user',source:{kind:'user'},content:[{type:'text',text}]};
 return {agent:{session:{header:{id:'synthetic-session',origin:'user'},snapshotEvents:()=>[{type:'turn/start',data:{}},{type:'user/message',data:message}]}},signal,callId:id};
}
export async function fixture(){
 const {createLayeredMemory}=await load('host/layered-memory/index.js');
 const projects=[{key:'synthetic',root:'D:/synthetic-only',userProfile:'shared-synthetic'},{key:'other',root:'D:/other-only',userProfile:'shared-synthetic'}];
 const domains=new Map();let clock=Date.parse('2026-01-02T00:00:00.000Z'),sequence=0,publicationFailure=false,coldFailure=false;
 const facility={open:async spec=>{let tables=domains.get(spec.name);if(!tables){tables=new Map();domains.set(spec.name,tables);}return {table:name=>{let map=tables.get(name);if(!map){map=new Map();tables.set(name,map);}return {get:k=>structuredClone(map.get(k)),put:async(k,v)=>{if(spec.name==='dsh_four_layer_memory_v1'&&publicationFailure)throw Object.assign(new Error('synthetic-publication'),{code:'TEST_ACTIVE_WRITE'});if(spec.name==='dsh_four_layer_archive_v1'&&coldFailure)throw Object.assign(new Error('synthetic-cold'),{code:'TEST_COLD_WRITE'});spec.tables[name]?.valueSchema?.parse(v);map.set(k,structuredClone(v));},delete:async k=>map.delete(k),entries:()=>[...map.entries()].map(([k,v])=>[k,structuredClone(v)])};},close:async()=>{}};}};
 const layers=await createLayeredMemory({facility,scope:{projects},legacy:{read:()=>({memories:[],index:null})},now:()=>clock});
 const catalogMap=()=>domains.get('dsh_four_layer_memory_v1').get('active');
 const catalog=()=>structuredClone(catalogMap().get('catalog'));
 const mutate=fn=>{const state=catalog();fn(state);catalogMap().set('catalog',state);};
 const get=id=>layers.read(projects[0]).find(r=>r.id===id);
 async function save(text,key='deliverable.format',extra={},project=projects[0],id='save-'+(++sequence)){
  return layers.tools.save(project,{text,semanticKey:key,category:'project',status:'confirmed',eventId:id,reason:'Synthetic direct evidence',...extra},execution(text,id));
 }
 async function revise(record,extra={},id='revise-'+(++sequence),signal){const proof='确认采用并更正该记忆，已完成';return layers.tools.revise(projects[0],{id:record.id,expectedRevision:record.revision,eventId:id,reason:'Synthetic confirmation',text:record.text,status:'confirmed',...extra},execution(proof,id,signal));}
 async function remove(record,operation='archive',id='remove-'+(++sequence),signal){const proof=operation==='archive'?'归档该记忆':operation==='revoke'?'忘记并撤回该记忆':'永久删除该记忆，彻底删除';return layers.tools[operation](projects[0],{id:record.id,expectedRevision:record.revision,eventId:id,reason:'Synthetic explicit exit'},execution(proof,id,signal));}
 return {layers,projects,project:projects[0],domains,catalog,mutate,get,save,revise,remove,setClock:value=>{clock=value;},advance:days=>{clock+=days*day;},now:()=>clock,failPublication:value=>{publicationFailure=value;},failCold:value=>{coldFailure=value;},close:()=>layers.close()};
}
export async function conflictFixture(){const f=await fixture();f.a=(await f.save('项目交付格式为 PDF')).record;f.b=(await f.save('项目交付格式为 Markdown')).record;return f;}

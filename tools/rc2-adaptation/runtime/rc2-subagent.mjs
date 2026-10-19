import {randomUUID} from 'node:crypto';
import {SessionId} from '@deepseek-ai/dsh-session';
const fail=code=>{throw Object.assign(Error(code),{code});};

// RC.2 presets own native tool composition. Install the suite restriction in
// the real child scope at creation; keep a root guard throughout publication
// and failed cleanup, before any child model or tool can execute.
export async function startSuiteActivation(ctx,input){
 if(typeof ctx.subagents?.startActivation!=='function')fail('SEP_RC2_SUBAGENT_UNAVAILABLE');
 const {signal,label,toolFilter,...request}=input;signal.throwIfAborted();
 if(!toolFilter||Object.keys(toolFilter).length!==1||!Array.isArray(toolFilter.allow)||toolFilter.allow.length>16||toolFilter.allow.some(n=>typeof n!=='string'||!n.length))fail('SEP_RC2_SUBAGENT_SCOPE');
 const childId=SessionId(randomUUID()),allow=new Set(toolFilter.allow);let scoped=false;
 const guard=ctx.tools.guard(exec=>exec.agent?.id===childId&&!allow.has(exec.name)?'P1_READONLY_CHILD':undefined);
 const unlisten=ctx.on('agent/created',({agent})=>{
  if(agent.id!==childId)return;
  agent.ctx.tools.restrict({allow:[...allow]});scoped=true;
 });
 let activation;
 try{activation=await ctx.subagents.startActivation({provider:'spawn',childId,label,signal,delivery:'caller',request});}
 catch(error){if(!ctx.agents.get(childId))guard();throw error;}
 finally{unlisten();}
 let closed=false,closing;
 const dispose=()=>{
  if(closed)return Promise.resolve();
  if(closing)return closing;
  closing=Promise.resolve().then(()=>activation.dispose()).then(()=>{closed=true;guard();signal.removeEventListener('abort',abort);}).finally(()=>{closing=undefined;});
  return closing;
 };
 const abort=()=>{void dispose().catch(()=>{});};
 if(!scoped){await dispose();fail('SEP_RC2_SUBAGENT_SCOPE');}
 signal.addEventListener('abort',abort,{once:true});if(signal.aborted)abort();
 const result=activation.result.finally(()=>signal.removeEventListener('abort',abort));void result.catch(()=>{});
 return {id:activation.childId,result,dispose};
}

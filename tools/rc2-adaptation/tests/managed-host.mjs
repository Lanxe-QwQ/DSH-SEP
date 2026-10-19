// Actual managed RC.2 Host. Blank credential; no external model calls.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
const base=process.argv[2],f=JSON.parse(await readFile(join(base,'FIXTURE.json'))),runs=[],report={schema:1,status:'fail',modelCalls:0,scope:'Actual managed Host with synthetic new-install profile; not Electron or installation proof',rounds:[],resourceAudit:{status:'not_run'}};
let current;
const load=p=>import(pathToFileURL(p));
const bounded=(promise,ms)=>{let t;return Promise.race([promise,new Promise((_,j)=>{t=setTimeout(()=>j(Error('TEST_DEADLINE')),ms);})]).finally(()=>clearTimeout(t));};
const {openDaily,loadDeployment}=await load(f.launcher),{startCoordinated}=await load(join(dirname(f.launcher),'startup-coordinator.mjs'));
async function start(round){const owned={round,spawns:[]};runs.push(owned);current=owned;owned.runtime=await bounded(startCoordinated(f.configPath,{loadDeployment,readCredential:false,openDaily:(path,opts)=>openDaily(path,{...opts,onHostSpawn:({child,generation})=>{const row={pid:child.pid,generation,out:[],err:[],exit:null};owned.spawns.push(row);child.stdout.on('data',b=>row.out.push(b));child.stderr.on('data',b=>row.err.push(b));child.once('close',(code,signal)=>{row.exit={code,signal};});}})}),180000);return owned;}
async function stop(o){if(o.closed)return;await bounded(o.runtime.close(),60000);for(const row of o.spawns){assert(row.exit);assert.equal(row.exit.code,0);assert.throws(()=>process.kill(row.pid,0),{code:'ESRCH'});}o.closed=true;}
try{
 for(let round=1;round<=2;round++){
  const o=await start(round),s=await o.runtime.client.call('status');assert.equal(s.guardian.phase,'running');assert.equal(s.writerState,'open');
  const ready=await o.runtime.client.call('desktopReady');assert.equal(new URL(ready.url).hostname,'127.0.0.1');
  const inspection=await o.runtime.client.call('desktopQuitInspection');assert.equal(inspection.activeTasks,false);assert.equal(inspection.scheduledTasks,false);
  const {openHttpCarrier}=await load(join(f.program,'node_modules/@deepseek-ai/dsh-recovery/src/http-carrier.mjs'));const carrier=await openHttpCarrier(ready);
  try{const r=await carrier.fetch(new Request('dsh-app://app/api/sep-budget/list',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({type:'client-request',rpcId:'rc2-budget-'+round,method:'sep-budget/list',payload:{}}),signal:AbortSignal.timeout(15000)}));assert.equal(r.status,200);const b=await r.json();assert.equal(b.result.ok,true,JSON.stringify(b));assert.equal(b.result.value.defaults.limitCny,100);assert.equal(b.result.value.shared.accountedUpperBoundCny,0);}finally{carrier.close();}
  await stop(o);report.rounds.push({round,status:'pass',pid:s.guardian.pid,inspection,closed:true});current=null;
 }
 report.status='pass';report.resourceAudit={status:'pass',path:'Both owned Host lifetimes closed normally; tracked exact PID exit0 and absence confirmed. No forced cleanup.'};
}catch(e){report.error={code:e.code??e.name,message:String(e.message).slice(0,1200)};process.exitCode=1;}
finally{
 if(current?.runtime&&!current.closed)try{await stop(current);report.resourceAudit={status:'pass',path:'Subsequent test cleanup after failure, via runtime.close; acceptance remains fail.'};}catch(e){report.resourceAudit={status:'blocked',code:e.code??e.name};}
 for(const o of runs)for(const r of o.spawns){await writeFile(join(base,`host-${o.round}-${r.generation}-${process.env.SEP_TEST_LOG_GENERATION??'r1'}.stdout.log`),Buffer.concat(r.out),{flag:'wx'});await writeFile(join(base,`host-${o.round}-${r.generation}-${process.env.SEP_TEST_LOG_GENERATION??'r1'}.stderr.log`),Buffer.concat(r.err),{flag:'wx'});}
 await writeFile(join(base,'MANAGED-HOST-'+(process.env.SEP_TEST_LOG_GENERATION??'r1')+'.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(report));
}

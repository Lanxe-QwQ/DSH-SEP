import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,cp} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {createHash} from 'node:crypto';

const [stageInput]=process.argv.slice(2);assert(stageInput);
const outputName=process.argv[3]??'candidate-source';assert(/^candidate-source(?:-replay-r[1-9][0-9]*)?$/.test(outputName));
const stage=resolve(stageInput),baseline=join(stage,'baseline-runtime'),out=join(stage,outputName);
const host=join(stage,'host-rc2'),hash=b=>createHash('sha256').update(b).digest('hex');
const input=JSON.parse(await readFile(join(stage,'evidence/INPUTS.json')));
assert.equal(input.officialSourceCommit,'687f282e8625c6b8d11ff58211a90524be2e4317');
const baselineRecord=JSON.parse(await readFile(join(stage,'evidence/BASELINE-RUNTIME.json')));
for(const row of baselineRecord.files)assert.equal(hash(await readFile(join(baseline,row.path))),row.sha256);
await mkdir(out);
for(const row of baselineRecord.files){const path=join(out,row.path),bytes=await readFile(join(baseline,row.path));assert.equal(hash(bytes),row.sha256);await mkdir(join(path,'..'),{recursive:true});await writeFile(path,bytes,{flag:'wx'});}
const files=[];
async function change(path,transforms){
 const before=await readFile(join(out,path));let code=before.toString();
 for(const t of transforms){assert.equal(code.split(t.from).length-1,t.count,'RC2_ANCHOR:'+path);code=code.split(t.from).join(t.to);}
 await writeFile(join(out,path),code);
 files.push({path,kind:'replayed-transform',sourceSha256:hash(before),resultSha256:hash(code),transforms});
}
for(const path of ['bundle/lib/session-persistence.js','bundle/lib/file-protection.js','bundle/lib/protected-file-tools.js'])
 await change(path,[{from:"'0.2.1-alpha.2'",to:"'0.2.1-rc.2'",count:1}]);

// Capture the complete released RC.2 implementation, retaining the native
// resource-owning plugin and injecting the SEP subclass into its service fiber.
const nativeDir=join(host,'node_modules/@deepseek-ai/dsh-session-persistence-jsonl/lib');
let native=await readFile(join(nativeDir,'index.js'));let code=native.toString();
const transforms=[
 {from:'"@deepseek-ai/dsh-session-format-catalog"',to:'"../../lib/session-catalog.js"',count:1},
 {from:'"@deepseek-ai/dsh-session"',to:'"../../lib/session-vocabulary.js"',count:1},
 {from:'"@deepseek-ai/dsh-session-persistence"',to:'"../../lib/session-storage-validation.js"',count:1},
 {from:'async function apply(ctx, config) {',to:'async function apply(ctx, config, Backend = JsonlSessionPersistence) {',count:1},
 {from:'new JsonlSessionPersistence(serviceCtx, config, tracker);',to:'new Backend(serviceCtx, config, tracker);',count:1},
 {from:'export { Config, JsonlCompressionSchema, apply, name };',to:'export { Config, JsonlCompressionSchema, JsonlSessionPersistence, apply, name };',count:1},
];
for(const t of transforms){assert.equal(code.split(t.from).length-1,t.count,'RC2_JSONL_ANCHOR');code=code.split(t.from).join(t.to);}
await writeFile(join(out,'bundle/host/session-jsonl/index.js'),code);
files.push({path:'bundle/host/session-jsonl/index.js',kind:'official-rc2-capture',officialPackage:'@deepseek-ai/dsh-session-persistence-jsonl@0.2.1-rc.2',sourceSha256:hash(native),resultSha256:hash(code),transforms});
let worker=await readFile(join(nativeDir,'worker.cjs'));let workerCode=worker.toString();
const workerTransform={from:')("../package.json")',to:') ("@deepseek-ai/dsh-llm/package.json")',count:1};
assert.equal(workerCode.split(workerTransform.from).length-1,1,'RC2_WORKER_ANCHOR');workerCode=workerCode.replace(workerTransform.from,workerTransform.to);
await writeFile(join(out,'bundle/host/session-jsonl/worker.cjs'),workerCode);
files.push({path:'bundle/host/session-jsonl/worker.cjs',kind:'official-rc2-capture',officialPackage:'@deepseek-ai/dsh-session-persistence-jsonl@0.2.1-rc.2',sourceSha256:hash(worker),resultSha256:hash(workerCode),transforms:[workerTransform]});

await change('bundle/lib/project-binding.js',[{from:"import SepSessionPersistence from './session-persistence.js';",to:"import {SepSessionPersistence} from './session-persistence.js';",count:1}]);
await change('bundle/lib/session-parent-proof.js',[{from:"import JsonlSessionPersistence from '../host/session-jsonl/index.js';",to:"import {JsonlSessionPersistence} from '../host/session-jsonl/index.js';",count:1}]);

await change('bundle/lib/session-persistence.js',[
 {from:"import JsonlSessionPersistence from '../host/session-jsonl/index.js';",to:"import {JsonlSessionPersistence,Config,apply as mountNativeJsonl} from '../host/session-jsonl/index.js';",count:1},
 {from:'export default class SepSessionPersistence extends JsonlSessionPersistence{',to:'export class SepSessionPersistence extends JsonlSessionPersistence{',count:1},
 {from:'constructor(ctx,config){',to:'constructor(ctx,config,tracker){',count:1},
 {from:'super(ctx,config);',to:'super(ctx,config,tracker);',count:1},
]);
const persistence=join(out,'bundle/lib/session-persistence.js');const before=await readFile(persistence);
const extra="\n// Retain the RC.2 provider's consumer-before-storage shutdown ordering.\nexport {Config};\nexport const name='dsh-sep-session-persistence';\nexport function apply(ctx,config){return mountNativeJsonl(ctx,config,SepSessionPersistence);}\nexport default {name,Config,apply};\n";
await writeFile(persistence,Buffer.concat([before,Buffer.from(extra)]));
files.push({path:'bundle/lib/session-persistence.js',kind:'append',sourceSha256:hash(before),resultSha256:hash(await readFile(persistence)),append:extra});

const bridgePath='bundle/host/p1-policy/alpha2-subagent.js';
const bridgeBefore=await readFile(join(out,bridgePath)),bridge=await readFile(new URL('./runtime/rc2-subagent.mjs',import.meta.url));
await writeFile(join(out,bridgePath),bridge);
files.push({path:bridgePath,kind:'owned-rc2-bridge',sourceSha256:hash(bridgeBefore),resultSha256:hash(bridge),currentSource:'tools/rc2-adaptation/runtime/rc2-subagent.mjs'});

const manifestPath=join(out,'package.json'),oldManifest=await readFile(manifestPath),manifest=JSON.parse(oldManifest);
manifest.version='0.2.1-beta.3-rc2-adapter.1';
manifest.engines={...manifest.engines,dsh:'0.2.1-rc.2'};
const inventory=JSON.parse(await readFile(join(stage,'SOURCE-INVENTORY-ARCHIVE.json')));
for(const name of Object.keys(manifest.peerDependencies??{})){
 const released=inventory.manifests[name];
 if(released&&!released.private)manifest.peerDependencies[name]=released.version;
}
manifest.peerDependencies['@deepseek-ai/dsh-invariants']='0.2.0-rc.2 || 0.2.1-rc.2';
manifest.files=[...new Set([...manifest.files,'RC2-ADAPTATION.json'])];
manifest.dshSepBundle.rc2CandidateContract='./RC2-ADAPTATION.json';
await writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n');
files.push({path:'package.json',kind:'manifest',sourceSha256:hash(oldManifest),resultSha256:hash(await readFile(manifestPath)),note:'Exact RC.2 host and released peers; legacy invariant leaf remains exact 0.2.0-rc.2, no range exemption.'});
for(const path of ['bundle/host/session-jsonl/origin.json']){
 const before=await readFile(join(out,path));
 await writeFile(join(out,path),JSON.stringify({schema:2,status:'superseded-for-rc2-isolated-candidate',currentOrigin:'RC2-ADAPTATION.json',baselineOriginSha256:hash(before),historicalOrigin:JSON.parse(before)},null,2)+'\n');
 files.push({path,kind:'origin-supersession',sourceSha256:hash(before),resultSha256:hash(await readFile(join(out,path)))});
}
const origin={schema:1,status:'not_run',scope:'RC.2 isolated adaptation; no desktop, installer or full platform certification yet',baselineAssetSha256:baselineRecord.sourceAssetSha256,host:{version:input.officialHostVersion,commit:input.officialSourceCommit},files};
await writeFile(join(out,'RC2-ADAPTATION.json'),JSON.stringify(origin,null,2)+'\n');
await writeFile(join(stage,'evidence',outputName==='candidate-source'?'RC2-RUNTIME-ORIGIN.json':'RC2-RUNTIME-ORIGIN-'+outputName+'.json'),JSON.stringify(origin,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'prepared',changes:files.length,version:manifest.version}));

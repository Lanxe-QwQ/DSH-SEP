import assert from 'node:assert/strict';
import{readFile,writeFile,readdir,lstat,rename}from'node:fs/promises';import{join,relative,resolve}from'node:path';import{pathToFileURL}from'node:url';import{createHash}from'node:crypto';
import{writeProgramGraph}from'../alpha2-desktop/daily-adaptation/build/program-graph.mjs';
import{auditBundle}from'../rc2-adaptation/windows-verification/bundle-audit.mjs';
const stage=resolve(process.argv[2]);assert.match(stage,/^D:\\AIData\\ProjectWork\\DSH\\beta5-publication-20261022-r1$/i);
const base=join(stage,'windows'),full=join(base,'bundle-full'),program=join(full,'payload'),old=JSON.parse(await readFile(join(full,'manifest.json'))),sha=b=>createHash('sha256').update(b).digest('hex');
const g=await writeProgramGraph(program),{writeDesktopRuntime,verifyDesktopRuntime}=await import(pathToFileURL(join(program,'build-runtime-helper.mjs')));
const d=JSON.parse(await readFile(join(full,'desktop-runtime.json')));writeDesktopRuntime(program,d.release,d.sharedPackages.map(p=>p.name),{platform:'win32',arch:'x64'});await verifyDesktopRuntime(program,'0.2.1-rc.2',{platform:'win32',arch:'x64'});
const graphBytes=await readFile(join(program,'graph.json')),descBytes=await readFile(join(program,'desktop-runtime.json'));
const record=(path,b)=>({path,size:b.length,sha256:sha(b),mode:420}),graph=record('graph.json',graphBytes),descriptor=record('desktop-runtime.json',descBytes);
// Generated circular-exclusion manifests live at bundle root, never payload.
await rename(join(program,'graph.json'),join(full,'graph-new.json'));await rename(join(program,'desktop-runtime.json'),join(full,'descriptor-new.json'));
const results=[];
for(const kind of ['full','sep']){
 const root=join(base,'bundle-'+kind),m=JSON.parse(await readFile(join(root,'manifest.json'))),required=new Set(m.required.map(f=>f.path)),map=new Map(g.graph.files.map(f=>[f.path,f]));
 for(const f of m.required){assert.deepEqual(map.get(f.path),{path:f.path,size:f.size,sha256:f.sha256,mode:f.mode},'official donor changed: '+f.path);}
 assert.equal(m.graph.sha256,old.graph.sha256);
 const launcher=join(root,'managed/bootstrap/launcher.mjs'),bytes=await readFile(launcher,'utf8');assert.equal(bytes.split(old.graph.sha256).length,2);await writeFile(launcher,bytes.replace(old.graph.sha256,graph.sha256));
 const originPath=join(root,'managed/bootstrap/ORIGIN.json'),origin=JSON.parse(await readFile(originPath));origin.graphHash=graph.sha256;origin.distributionVersion='0.2.1-beta.5';origin.memoryRepairBuild='beta4-memory-repair.1';await writeFile(originPath,JSON.stringify(origin,null,2)+'\n');
 const payload=kind==='full'?g.graph.files:g.graph.files.filter(f=>!required.has(f.path));
 const support=[];async function walk(dir){for(const n of(await readdir(dir)).sort()){const p=join(dir,n),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p);else{assert(s.isFile()&&s.nlink===1);const path=relative(root,p).replaceAll('\\','/');if(path.startsWith('payload/')||['manifest.json','graph.json','desktop-runtime.json','graph-new.json','descriptor-new.json'].includes(path))continue;const b=await readFile(p),previous=m.support.find(r=>r.path===path);assert(previous,'unexpected support '+path);support.push({...previous,size:b.length,sha256:sha(b)});}}}await walk(root);
 await writeFile(join(root,'graph.json'),graphBytes);await writeFile(join(root,'desktop-runtime.json'),descBytes);
 await writeFile(join(root,'manifest.json'),JSON.stringify({...m,graph,descriptor,payload,support},null,2)+'\n');
 results.push({kind,graphSha256:graph.sha256,descriptorSha256:descriptor.sha256,payloadFiles:payload.length,donorFiles:m.required.length,supportFiles:support.length});
}
// Move temporary generated manifests outside the install archive boundary.
await rename(join(full,'graph-new.json'),join(base,'graph.json'));await rename(join(full,'descriptor-new.json'),join(base,'desktop-runtime.json'));
for(const kind of ['full','sep']){const a=await auditBundle(join(base,'bundle-'+kind),{hostVersion:old.hostVersion,sepVersion:old.sepVersion,revision:old.revision});results.find(r=>r.kind===kind).audit={status:a.status,manifestSha256:a.manifestSha256,archiveRegularFiles:a.archiveRegularFiles};}
await writeFile(join(base,'SEALED.json'),JSON.stringify({schema:1,status:'pass',distributionVersion:'0.2.1-beta.5',internalBuild:'beta4-memory-repair.1',results},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(results));

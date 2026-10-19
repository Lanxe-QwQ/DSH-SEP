import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {join,resolve,relative,sep} from 'node:path';
import {mkdir,cp,readFile,writeFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const stage=resolve(process.argv[2]),generation=process.argv[3];assert(/^r[1-9][0-9]*$/.test(generation));
const source=join(stage,'desktop-source'),host=join(stage,'host-rc2'),out=join(stage,'windows-runtime-'+generation);
const require=createRequire(join(host,'package.json')),{build}=await import(pathToFileURL(require.resolve('esbuild')));
const hash=b=>createHash('sha256').update(b).digest('hex');await mkdir(out);
const helper=join(out,'build-runtime-helper.mjs');
await build({stdin:{contents:`export {writeDesktopRuntime,verifyDesktopRuntime} from ${JSON.stringify(join(source,'apps/desktop/src/runtime-tree.ts'))};export {desktopRuntimeFileExclusion} from ${JSON.stringify(join(source,'apps/desktop/scripts/runtime-file-policy.ts'))};`,resolveDir:source},outfile:helper,bundle:true,platform:'node',format:'esm',packages:'external',alias:{semver:require.resolve('semver')}});
const {writeDesktopRuntime,verifyDesktopRuntime,desktopRuntimeFileExclusion}=await import(pathToFileURL(helper));
const modules=join(host,'node_modules'),platform={platform:'win32',arch:'x64'};
await cp(modules,join(out,'node_modules'),{recursive:true,dereference:true,filter:path=>desktopRuntimeFileExclusion(relative(modules,path),platform,'win32-x64')===undefined});
const desktop=join(out,'node_modules/@deepseek-ai/dsh-desktop'),desktopHost=join(out,'node_modules/@deepseek-ai/dsh-desktop-host');
await cp(join(stage,'integrated-desktop-r2/app'),desktop,{recursive:true,filter:path=>!relative(join(stage,'integrated-desktop-r2/app'),path).split(sep).includes('node_modules')});
await cp(join(stage,'integrated-desktop-r2/desktop-host'),desktopHost,{recursive:true});
for(const [app,folder] of [['desktop',desktop],['desktop-host',desktopHost]]){
 const manifest=JSON.parse(await readFile(join(source,'apps',app,'package.json')));delete manifest.devDependencies;delete manifest.scripts;
 for(const group of ['dependencies','peerDependencies'])for(const [name,range]of Object.entries(manifest[group]??{}))if(range.startsWith('workspace:'))manifest[group][name]=JSON.parse(await readFile(join(out,'node_modules',name,'package.json'))).version;
 if(app==='desktop')manifest.dependencies.yauzl='3.4.0';
 await writeFile(join(folder,'package.json'),JSON.stringify(manifest,null,2)+'\n');
}
for(const name of ['ui-settings-general','ui-settings-account','ui-chat','ui-settings','remotes']){
 const target=join(out,'node_modules/@deepseek-ai/dsh-'+(name==='remotes'?'api-remotes':'client-'+name),'lib');
 await cp(join(stage,'integrated-client-r3',name),target,{recursive:true});
}
const recovery=join(out,'node_modules/@deepseek-ai/dsh-recovery'),recoveryHelper=join(stage,'source/tools/alpha2-desktop/daily-adaptation/build/daily-recovery.mjs');
const {buildDailyRecovery}=await import(pathToFileURL(recoveryHelper));
await buildDailyRecovery({coreRoot:join(out,'node_modules/dsh-sep-bundle'),out:recovery,leaseSource:join(stage,'source/tools/alpha2-desktop/daily-adaptation/lib/project-write-lease.mjs')});
const guardianPath=join(recovery,'src/guardian.mjs'),guardian=await readFile(guardianPath,'utf8');assert.equal(guardian.split("'0.2.1-alpha.2'").length-1,1);await writeFile(guardianPath,guardian.replace("'0.2.1-alpha.2'","'0.2.1-rc.2'"));
const recoveryManifest=JSON.parse(await readFile(join(recovery,'package.json')));recoveryManifest.version=recoveryManifest.version.replace('-daily.alpha2.1','-daily.rc2.1');
for(const name of Object.keys(recoveryManifest.peerDependencies??{}))if(name.startsWith('@deepseek-ai/dsh-')&&name!=='@deepseek-ai/dsh-invariants')recoveryManifest.peerDependencies[name]='0.2.1-rc.2';
await writeFile(join(recovery,'package.json'),JSON.stringify(recoveryManifest,null,2)+'\n');
const brand=join(out,'node_modules/dsh-sep-brand');await cp(join(out,'node_modules/dsh-sep-bundle/bundle/modules/sep-brand'),brand,{recursive:true});
const brandManifest=JSON.parse(await readFile(join(brand,'package.json')));brandManifest.peerDependencies={'@deepseek-ai/cordis':'4.0.5','@deepseek-ai/dsh-client-ui-sidebar':'0.2.1-rc.2'};await writeFile(join(brand,'package.json'),JSON.stringify(brandManifest,null,2)+'\n');
const manifest=JSON.parse(await readFile(join(host,'package.json')));manifest.name='dsh-sep-rc2-isolated-runtime';delete manifest.devDependencies;
manifest.dependencies['dsh-sep-bundle']='0.2.1-beta.3-rc2-adapter.1';manifest.dependencies['@deepseek-ai/dsh-desktop']='0.2.1-rc.2';manifest.dependencies['@deepseek-ai/dsh-desktop-host']='0.2.1-rc.2';manifest.dependencies['@deepseek-ai/dsh-recovery']=recoveryManifest.version;
manifest.dependencies['dsh-sep-brand']=brandManifest.version;
await writeFile(join(out,'package.json'),JSON.stringify(manifest,null,2)+'\n');
const {buildDailyComposition}=await import(new URL('../runtime/daily-composition.mjs',import.meta.url));
await buildDailyComposition({coreRoot:join(out,'node_modules/dsh-sep-bundle'),out:join(out,'daily-adapter')});
const {writeProgramGraph}=await import(new URL('../../alpha2-desktop/daily-adaptation/build/program-graph.mjs',import.meta.url));
await writeProgramGraph(out);
const names=[];for(const name of await readdir(join(out,'node_modules/@deepseek-ai'))){try{const m=JSON.parse(await readFile(join(out,'node_modules/@deepseek-ai',name,'package.json')));if(m.name)names.push(m.name);}catch(e){if(e.code!=='ENOENT')throw e;}}
const descriptor=writeDesktopRuntime(out,{schemaVersion:1,version:'0.2.1-rc.2',hostProtocolVersion:4,nodeVersion:'24.19.0',pnpmVersion:'11.25.0'},[...names,'dsh-sep-brand'],platform);await verifyDesktopRuntime(out,'0.2.1-rc.2',platform);
const receipt={schema:1,status:'pass',scope:'RC.2 immutable program graph assembled and verified; desktop lifecycle and installation not yet verified',output:out,files:descriptor.files.length,sharedPackages:descriptor.sharedPackages.length,descriptorSha256:hash(await readFile(join(out,'desktop-runtime.json'))),dailyChanged:false};
await writeFile(join(stage,'evidence/WINDOWS-RUNTIME-'+generation+'.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(receipt));

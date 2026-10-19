// Synthetic, private isolated instance. Never imports live daily data.
import assert from 'node:assert/strict';
import {join,resolve,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {mkdir,readFile,writeFile,cp} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildDailyLauncher} from '../build/daily-launcher.mjs';
import {adaptDailyPresets} from '../runtime/daily-presets.mjs';
const stage=resolve(process.argv[2]),gen=process.argv[3];assert(/^r[1-9][0-9]*$/.test(gen));
const program=join(stage,'windows-runtime-r3'),base=join(stage,'windows-desktop-'+gen),repo=join(stage,'source');
const sha=b=>createHash('sha256').update(b).digest('hex');await mkdir(base);
const inputSource=join(repo,'tools/alpha2-windows/installer/fresh-profile.mjs'),before=await readFile(inputSource,'utf8');
await cp(join(repo,'tools/alpha2-windows/installer/daily-profile.mjs'),join(base,'daily-profile.mjs'));
let code=before.replace("const program=join(destination,'program')",`const program=${JSON.stringify(program)}`);const from="await save(join(profileRoot,'cordis.patch.yml'),converted.patches);";
assert.equal(code.split(from).length,2);code=code.replace(from,`const {createRequire}=await import('node:module');const require=createRequire(join(program,'package.json'));const {loadOverlayPatches}=await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-app-boot')));const nativeRows=['standard','cordis','minimal','ptc'].map(name=>loadOverlayPatches('dsh',join(program,'node_modules/@deepseek-ai/dsh-web-app/presets',name+'.patch.yml'))[0].insert[0]);await save(join(profileRoot,'cordis.patch.yml'),[...adaptDailyPresets(nativeRows),...converted.patches]);`);
code=`import {pathToFileURL} from 'node:url';\nimport {adaptDailyPresets} from ${JSON.stringify(new URL('../runtime/daily-presets.mjs',import.meta.url).href)};\n`+code;
await writeFile(join(base,'fresh-profile.mjs'),code,{flag:'wx'});
const {auditDesktopPayload}=await import(pathToFileURL(join(repo,'tools/offline-upgrade-bridge-beta2/operator/shared/sep-update/runtime/launcher/desktop-payload.mjs')));
const support='D:/AIData/ProjectWork/DSH/alpha2-windows-packages-20261015-r1/support';
const desktopRuntimeRoot=join(support,'runtime/desktop');
const desktop={schema:1,platform:'win32-x64',version:'44.7.0',executable:'electron.exe',...await auditDesktopPayload(desktopRuntimeRoot)};
const manifest={hostVersion:'0.2.1-rc.2',sepVersion:'0.2.1-beta.3-rc2-adapter.1',graph:{sha256:sha(await readFile(join(program,'graph.json')))},descriptor:{sha256:sha(await readFile(join(program,'desktop-runtime.json')))},desktop};
const {createFreshProfile}=await import(pathToFileURL(join(base,'fresh-profile.mjs')));
const fresh=await createFreshProfile({destination:base,manifest});
const c=fresh.config;c.releaseRoot=program;c.nodeExecutable=process.execPath;c.desktopRuntimeRoot=desktopRuntimeRoot;c.pnpmEntry=resolve(process.env.SEP_TEST_PNPM_ENTRY??(()=>{throw Error('SEP_TEST_PNPM_ENTRY_REQUIRED')})());
// The generated selection binds actual immutable program paths; createFreshProfile
// normally receives an installed program/ child. Rebind this synthetic external
// immutable graph explicitly, before any host is started.
const sel=JSON.parse(await readFile(c.dailySelectionPath)),old=join(base,'program');
const rebase=x=>typeof x==='string'?x.replaceAll(old,program):Array.isArray(x)?x.map(rebase):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).map(([k,v])=>[k,rebase(v)])):x;
const selected=rebase(sel),bindings=[join(program,'node_modules/dsh-sep-bundle/package.json'),...['package.json','ORIGIN.json','native-settings-installation.js','settings-runtime.js','protected-profile.js','protected-file-tools.js','file-protection.js','project-binding.js'].map(n=>join(program,'daily-adapter',n))];selected.bindings=[];for(const path of bindings)selected.bindings.push({path,sha256:sha(await readFile(path))});
const selBytes=JSON.stringify(selected)+'\n';await writeFile(c.dailySelectionPath,selBytes);c.dailySelectionSha256=sha(selBytes);
const patchFile=join(c.profileRoot,'cordis.patch.yml');await writeFile(patchFile,JSON.stringify(rebase(JSON.parse(await readFile(patchFile))))+'\n');
await cp(join(support,'runtime/primary-runtime'),join(base,'runtime/primary-runtime'),{recursive:true});
await cp(join(stage,'official-source/packages/skill/skill-office/assets'),join(base,'runtime/office-skills'),{recursive:true});
const {openControl}=await import(pathToFileURL(join(program,'node_modules/dsh-sep-bundle/bundle/modules/system-enhancement-package/src/p2/control.js')));const control=await openControl({storageRoot:c.storageRoot,mode:'maintenance',initialize:true});await control.close();
const {Budget}=await import(pathToFileURL(join(program,'node_modules/dsh-sep-bundle/bundle/modules/system-enhancement-package/src/budget-ledger.js')));await new Budget(fresh.budgetPath,{limit:100,initialSpent:0,taskLimitCny:5}).init();
await writeFile(fresh.configPath,JSON.stringify(c,null,2)+'\n');
const launcher=join(base,'managed/bootstrap');await buildDailyLauncher({sourceRoot:join(repo,'tools/offline-upgrade-bridge-beta2/operator/shared/sep-update/runtime/launcher'),out:launcher,graphHash:c.graphHash,adapterSource:join(repo,'tools/alpha2-desktop/daily-adaptation')});
// Set the test-only observer outside the immutable program; production main
// remains unchanged. Network release results are synthetic in this observer.
const probe=join(base,'external-probe');await mkdir(probe);await writeFile(join(probe,'package.json'),JSON.stringify({type:'module',main:'probe-bootstrap.mjs'})+'\n');
await cp(join(repo,'tools/alpha2-desktop/daily-adaptation/tests/desktop-probe-bootstrap.mjs'),join(probe,'probe-bootstrap.mjs'));
const receipt=join(base,'DESKTOP-LIFECYCLE.json');await writeFile(join(probe,'sep-test-input.json'),JSON.stringify({appRoot:join(program,'node_modules/@deepseek-ai/dsh-desktop'),desktopMain:join(program,'node_modules/@deepseek-ai/dsh-desktop/lib/main.js'),userData:c.electronUserData,project:c.projects[0].root,receipt,notVerified:['physical pointer drag','first-close native prompt','physical tray click','paid online API']})+'\n');
await writeFile(join(c.electronUserData,'background-close-confirmed'),'synthetic preconfirmation; real notice separately not_run\n');
await writeFile(join(base,'FIXTURE.json'),JSON.stringify({schema:1,status:'not_run',base,program,config:c,configPath:fresh.configPath,launcher:join(launcher,'launcher.mjs'),probe,receipt,credential:'blank .env',origin:{source:inputSource,sourceSha256:sha(before),resultSha256:sha(code),from,to:'RC.2 reviewed preset overlays added before native profile rows'}},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'prepared',base,config:fresh.configPath,modelCalls:0}));

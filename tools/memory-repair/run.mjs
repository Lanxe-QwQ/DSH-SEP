// Portable reproduction runner. Output directory must be new and physically
// resolved; caller supplies a synthetic-only native host and dependency tree.
import {readFile,writeFile,mkdir,realpath,readdir,lstat} from 'node:fs/promises';
import {join,resolve,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const repo=resolve(fileURLToPath(new URL('../..',import.meta.url))),mode=process.argv[2]??'core',out=resolve(process.argv[3]);
assert.equal(await realpath(dirname(out)),dirname(out),'output parent must be a physical path');await mkdir(out,{mode:0o700});
const core=['conflicts','tokenizer','usage','eligibility'],names=mode==='storage'?['storage']:mode==='core'?core:mode==='integration'?['integration']:mode==='existing'?[]:null;assert(names,'unsupported mode');
const bundle=resolve(process.env.SEP_MEMORY_BUNDLE??join(repo,'tools/rc2-adaptation/candidate/bundle')),files=mode==='existing'?[join(repo,'tools/rc2-adaptation/tests/shared-consumers.test.mjs'),join(repo,'tools/bundle-install/tests/review-regressions.test.mjs')]:names.map(name=>join(import.meta.dirname,'tests',name+'.test.mjs'));
const sha=b=>createHash('sha256').update(b).digest('hex'),inputs=[];async function record(p,label){const b=await readFile(p);inputs.push({path:label,bytes:b.length,sha256:sha(b)});}
for(const p of [...files,join(import.meta.dirname,'tests/fixture.mjs'),fileURLToPath(import.meta.url)])await record(p,relative(repo,p).replaceAll('\\','/'));
async function walk(dir){for(const name of(await readdir(dir)).sort()){const p=join(dir,name),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p);else await record(p,'installed-bundle/'+relative(bundle,p).replaceAll('\\','/'));}}await walk(bundle);
const input={schema:1,mode,inputs,node:process.version,platform:process.platform,arch:process.arch,syntheticDataOnly:true};await writeFile(join(out,'INPUTS.json'),JSON.stringify(input,null,2)+'\n',{flag:'wx',mode:0o600});
const env={...process.env,SEP_MEMORY_SOURCE:repo,SEP_SOURCE_REPO:repo,SEP_MEMORY_BUNDLE:bundle,SEP_BUNDLE_TEST_ROOT:out};delete env.DEEPSEEK_API_KEY;delete env.OPENAI_API_KEY;
const r=spawnSync(process.execPath,['--test','--test-reporter=tap',...files],{cwd:repo,env,encoding:'utf8',timeout:300000,maxBuffer:16*1024*1024}),log=r.stdout+'\n'+r.stderr;await writeFile(join(out,'tests.log'),log,{flag:'wx',mode:0o600});
const count=key=>Number(log.match(new RegExp('^# '+key+' (\\d+)','m'))?.[1]??0),receipt={schema:1,status:r.status===0?'pass':'fail',mode,platform:process.platform,arch:process.arch,exitCode:r.status,signal:r.signal,error:r.error?.code,tests:count('tests'),passed:count('pass'),failed:count('fail'),skipped:count('skipped'),logSha256:sha(log),inputSha256:sha(await readFile(join(out,'INPUTS.json'))),model:'synthetic/no paid model'};await writeFile(join(out,'RESULT.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx',mode:0o600});console.log(JSON.stringify(receipt));if(r.status!==0)console.error(log.slice(-12000));process.exitCode=r.status??1;

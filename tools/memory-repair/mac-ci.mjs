// Native repair verification only. This does not rebuild/sign a desktop app,
// install into a user's account, publish a Release, or contact a model API.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,realpath,readdir,lstat} from 'node:fs/promises';
import {createWriteStream} from 'node:fs';
import {join,resolve,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {pipeline} from 'node:stream/promises';
import {Readable,Transform} from 'node:stream';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const runFile=promisify(execFile),repo=resolve(fileURLToPath(new URL('../..',import.meta.url))),out=resolve(process.argv[2]);
assert.equal(process.platform,'darwin');assert.equal(process.arch,'arm64');assert.equal(process.version,'v24.21.0');assert.equal(await realpath(process.env.RUNNER_TEMP),dirname(out));
process.umask(0o077);await mkdir(out,{mode:0o700});
const sha=(b,algorithm='sha256')=>createHash(algorithm).update(b).digest('hex'),commands=[],env={PATH:process.env.PATH,HOME:process.env.HOME,TMPDIR:process.env.TMPDIR,RUNNER_TEMP:process.env.RUNNER_TEMP,LANG:'en_US.UTF-8',CI:'true',npm_config_ignore_scripts:'true'};
async function run(name,file,args,cwd=out,timeout=180000,extra={}){let r;try{r=await runFile(file,args,{cwd,env:{...env,...extra},timeout,maxBuffer:8*1024*1024});commands.push({name,status:'pass'});return r;}catch(error){r=error;commands.push({name,status:'fail',code:typeof error.code==='string'?error.code:'COMMAND_FAILED'});throw error;}finally{await writeFile(join(out,name+'.log'),(r?.stdout??'')+'\n'+(r?.stderr??''),{flag:'wx'});}}
let status='fail',diagnosis,step='verify-source';
try{
 const candidate=join(repo,'tools/rc2-adaptation/candidate'),manifest=JSON.parse(await readFile(join(repo,'tools/rc2-adaptation/CANDIDATE-SOURCE.json'))),indexed=new Set(manifest.files.map(r=>r.path));
 assert.equal(manifest.buildId,'beta4-memory-repair.1');for(const row of manifest.files){assert(!row.path.includes('\\')&&!row.path.startsWith('/')&&row.path.split('/').every(p=>p&&p!=='.'&&p!=='..'));const p=join(candidate,row.path),s=await lstat(p);assert(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1);const b=await readFile(p);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);}
 async function walk(dir){for(const n of await readdir(dir)){const p=join(dir,n),s=await lstat(p);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(p);else assert(indexed.has(relative(candidate,p).split('\\').join('/')));}}await walk(candidate);
 await run('system','/usr/bin/sw_vers',[]);
 // This exact pnpm tar/SHA512 is already fixed by the reviewed Mac carrier.
 step='fixed-package-manager';const archive=join(out,'pnpm.tgz'),response=await fetch('https://registry.npmjs.org/pnpm/-/pnpm-11.28.5.tgz',{redirect:'error',signal:AbortSignal.timeout(90000)});assert(response.ok);let bytes=0;const hash=createHash('sha512');
 await pipeline(Readable.fromWeb(response.body),new Transform({transform(b,_,next){bytes+=b.length;if(bytes>30000000)return next(Error('PACKAGE_TOO_LARGE'));hash.update(b);next(null,b);}}),createWriteStream(archive,{flags:'wx'}));assert.equal(hash.digest('base64'),'SEVj0wtMKtJ8tIqpT/KzAtvOvI/2vyiBbCWJiG4UbOf3bzVPO8GkOOb16XaMMCqgpvet2CMpA81M+BQmy8FNng==');
 const pmRoot=join(out,'pm');await mkdir(pmRoot);await run('pnpm-extract','/usr/bin/tar',['-xzf',archive,'-C',pmRoot]);const pm=JSON.parse(await readFile(join(pmRoot,'package/package.json')));assert.equal(pm.version,'11.28.5');const entry=resolve(pmRoot,'package',pm.bin.pnpm);assert(entry.startsWith(join(pmRoot,'package')+'/'));
 step='pack-and-lock';const artifacts=join(out,'artifacts');await mkdir(artifacts);await run('pack',process.execPath,[entry,'--config.ignore-scripts=true','pack','--pack-destination',artifacts],candidate);
 const packageManifest=JSON.parse(await readFile(join(candidate,'package.json'))),packageBytes=await readFile(join(artifacts,'dsh-sep-bundle-'+packageManifest.version+'.tgz'));await writeFile(join(out,'candidate.tgz'),packageBytes,{flag:'wx'});
 const host=join(out,'host');await mkdir(host);await writeFile(join(host,'package.json'),await readFile(join(repo,'tools/rc2-adaptation/macos/host-package.json')),{flag:'wx'});
 let lock=await readFile(join(repo,'tools/rc2-adaptation/macos/pnpm-lock.yaml'),'utf8'),changed=0;lock=lock.replace(/resolution: \{integrity: [^,\n]+, tarball: file:\.\.\/candidate\.tgz\}/g,()=>{changed++;return 'resolution: {integrity: sha512-'+createHash('sha512').update(packageBytes).digest('base64')+', tarball: file:../candidate.tgz}';});assert.equal(changed,1);await writeFile(join(host,'pnpm-lock.yaml'),lock,{flag:'wx'});await writeFile(join(host,'pnpm-workspace.yaml'),'packages:\n  - .\nautoInstallPeers: false\nnodeLinker: hoisted\nminimumReleaseAge: 1440\n',{flag:'wx'});
 step='install';await run('install',process.execPath,[entry,'install','--frozen-lockfile','--ignore-scripts','--config.store-dir='+join(out,'store'),'--config.cache-dir='+join(out,'cache')],host,900000);
 const installed=join(host,'node_modules/dsh-sep-bundle');const packChanges=[];for(const row of manifest.files){const b=await readFile(join(installed,row.path));if(sha(b)!==row.sha256){assert.equal(row.path,'package.json');const source=await readFile(join(candidate,row.path));assert(source.at(-1)===10&&b.equals(source.subarray(0,-1)),'only declared final LF removal allowed');packChanges.push({path:row.path,transform:'remove exactly one terminal LF',sourceSha256:row.sha256,resultSha256:sha(b)});}}
 await writeFile(join(out,'CANDIDATE.json'),JSON.stringify({schema:1,sourceCommit:process.env.GITHUB_SHA,candidateSha256:sha(packageBytes),installedFiles:manifest.files.length,packChanges,lockSha256:sha(lock),scope:'native common memory/JSON/P2 repair; not complete Mac application certification'},null,2)+'\n',{flag:'wx'});
 for(const mode of ['core','storage']){step=mode;await run(mode,process.execPath,[join(repo,'tools/memory-repair/run.mjs'),mode,join(out,mode)],repo,300000,{SEP_OFFICIAL_HARNESS:host,SEP_MEMORY_BUNDLE:join(installed,'bundle')});}status='pass';
}catch(error){diagnosis={step,code:/^[A-Z0-9_]{1,80}$/.test(error.code??'')?error.code:'MAC_REPAIR_VALIDATION_FAILED',.../^[A-Z0-9_]{1,80}$/.test(error.cause?.code??'')?{causeCode:error.cause.code}:{},errorType:error.name};process.exitCode=1;}
finally{await writeFile(join(out,'RESULT.json'),JSON.stringify({schema:1,status,diagnosis,commands,sourceCommit:process.env.GITHUB_SHA,platform:process.platform,arch:process.arch,notVerified:['new Mac desktop/install package','physical input','paid models','private library','daily deployment'],releasePublished:false},null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({status,diagnosis}));}

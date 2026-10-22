# Host-side operator. WSL interop/automount remain disabled; all work is D-backed.
from pathlib import Path
import subprocess,sys,json,base64,hashlib
repo=Path(__file__).resolve().parents[2];stage=repo.parent;out=stage/'linux-r2';out.mkdir()
files={}
for p in (repo/'tools/memory-repair').rglob('*'):
 if p.is_file() and (p.suffix=='.mjs') and 'evidence' not in p.parts:files[str(p.relative_to(repo)).replace('\\','/')]=base64.b64encode(p.read_bytes()).decode()
native=r"""
from pathlib import Path
import shutil,os,json,subprocess,hashlib,base64,tarfile
os.umask(0o077)
r=Path('/opt/dsh-sep-cross-platform/beta5-publication-20261022-r2');r.mkdir()
old=Path('/opt/dsh-sep-cross-platform/rc2-adaptation-20261018-r1/payload-r8');p=r/'payload'
node='/opt/dsh-sep-cross-platform/runtime/bin/node'
def run(name,args,env=None):
 x=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=900)
 (r/(name+'.stdout.log')).write_bytes(x.stdout);(r/(name+'.stderr.log')).write_bytes(x.stderr)
 assert x.returncode==0,(name,x.stdout[-2000:].decode(errors='replace'),x.stderr[-2000:].decode(errors='replace'))
 return x.stdout.decode()
oldhash=hashlib.sha256((old/'PAYLOAD-MANIFEST.json').read_bytes()).hexdigest()
run('verify-baseline',[node,'--input-type=module','-e',f"import{{verifyPayload}}from'{old}/src/linux-install.mjs';await verifyPayload('{old}','{oldhash}');"])
shutil.copytree(old,p,symlinks=True,ignore=lambda d,n:['PAYLOAD-MANIFEST.json'] if Path(d)==old else [])
repair=Path('/opt/dsh-sep-cross-platform/memory-repair-packed-20261021-r1/host/node_modules/dsh-sep-bundle')
bundle=p/'host/node_modules/dsh-sep-bundle';ui=bundle/'bundle/modules/ui-settings-memory/package.json';uiBytes=ui.read_bytes()
shutil.copytree(repair,bundle,dirs_exist_ok=True);ui.write_bytes(uiBytes)
(p/'README.md').write_text('# DSH SEP 0.2.1-beta.5 — Linux x64 preview\n\nThree memory fixes: query is not usage; Han bigrams preserve original boundaries; retired conflicts can be refreshed and confirmed. Reviewed build beta4-memory-repair.1. This is a fresh-install-only Beta, not full Linux certification.\n\n'+(old/'README.md').read_text())
build=json.loads((p/'BUILD.json').read_text());build.update(distributionVersion='0.2.1-beta.5',memoryRepairBuild='beta4-memory-repair.1',scope='Ubuntu 24.04 x64/ext4 isolated preview; historical private Sway evidence retained, full certification blocked');(p/'BUILD.json').write_text(json.dumps(build,indent=2)+'\n')
seal=json.loads(run('seal',[node,'--input-type=module','-e',f"import{{sealPayload,verifyPayload}}from'{p}/src/linux-install.mjs';const s=await sealPayload('{p}');await verifyPayload('{p}',s.sha256);console.log(JSON.stringify(s));"]))
archive=r/'DSH-SEP-0.2.1-beta.5-Linux-x64.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as t:t.add(p,arcname='DSH-SEP-Linux',recursive=True)
restored=r/'restored';restored.mkdir()
run('restore-exact-mode',['/usr/bin/tar','-xzpf',str(archive),'-C',str(restored)])
p=restored/'DSH-SEP-Linux';request={'payload':str(p),'destination':str(r/'installed'),'dataRoot':str(r/'data'),'manifestSha256':seal['sha256']};req=r/'request.json';req.write_text(json.dumps(request))
plan=json.loads(run('review',[node,str(p/'src/linux-install.mjs'),'review',str(req)]));assert plan['status']=='pass';request['planHash']=plan['planHash'];req.write_text(json.dumps(request));installed=json.loads(run('install',[node,str(p/'src/linux-install.mjs'),'install',str(req)]));assert installed['status']=='pass'
source=r/'source';source.mkdir()
for path,b in INPUTS.items():
 target=source/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(base64.b64decode(b))
host=r/'installed/host';env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ['KEY','TOKEN','SECRET','PASSWORD'])};env.update(SEP_OFFICIAL_HARNESS=str(host),SEP_MEMORY_BUNDLE=str(host/'node_modules/dsh-sep-bundle/bundle'))
results=[]
for mode in ['core','storage']:
 run('memory-'+mode,[node,str(source/'tools/memory-repair/run.mjs'),mode,str(r/('memory-'+mode))],env);result=json.loads((r/('memory-'+mode)/'RESULT.json').read_text());assert result['status']=='pass' and result['failed']==0 and result['skipped']==0;results.append(result)
h=hashlib.sha256()
with archive.open('rb')as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
result={'schema':1,'status':'pass','distributionVersion':'0.2.1-beta.5','archive':str(archive),'size':archive.stat().st_size,'sha256':h.hexdigest(),'baselineManifestSha256':oldhash,'manifestSha256':seal['sha256'],'installation':installed,'memory':results,'notVerified':['new physical input','paid models','full Linux certification']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
"""
script='INPUTS='+repr(files)+'\n'+native
args=['wsl.exe','-d','DSH-SEP-Linux-RC','-u','sep-rc','--','/usr/bin/python3','-c','import sys;exec(sys.stdin.buffer.read())']
x=subprocess.run(args,input=script.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=2400)
(out/'operator.stdout.log').write_bytes(x.stdout);(out/'operator.stderr.log').write_bytes(x.stderr)
assert x.returncode==0,x.stdout[-3000:].decode(errors='replace')+'\n'+x.stderr[-3000:].decode(errors='replace')
print(x.stdout.decode(errors='replace'))
# Export only the verified public archive and synthetic evidence through stdout.
result=json.loads(x.stdout.decode().strip().splitlines()[-1]);target=out/Path(result['archive']).name
with target.open('xb') as f:
 p=subprocess.run(['wsl.exe','-d','DSH-SEP-Linux-RC','-u','sep-rc','--','/bin/cat',result['archive']],stdout=f,stderr=subprocess.PIPE,timeout=900)
 assert p.returncode==0
assert target.stat().st_size==result['size']
h=hashlib.sha256()
with target.open('rb')as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
assert h.hexdigest()==result['sha256'];(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('Linux archive export verified')

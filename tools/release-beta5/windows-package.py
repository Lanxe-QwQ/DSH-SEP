# Public archive operator; no daily/private inputs.
from pathlib import Path
import json,hashlib,zipfile,subprocess,time
repo=Path(__file__).resolve().parents[2];stage=repo.parent;base=stage/'windows';node=Path(r'D:\AIData\ProjectWork\DSH\memory-daily-deployment-20261022-r1\daily-win\runtime\node\node.exe')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
# Build sealing runs independently; require its complete success before mutation.
end=time.monotonic()+1200
while not(base/'SEALED.json').exists():
 assert time.monotonic()<end,'SEAL_DEADLINE';time.sleep(2)
assert json.loads((base/'SEALED.json').read_text(encoding='utf8'))['status']=='pass'
assets=[]
for kind,label in [('full','Full'),('sep','Only')]:
 root=base/('bundle-'+kind);originPath=root/'managed/bootstrap/ORIGIN.json';raw=originPath.read_bytes();origin=json.loads(raw);graphHash=origin['graphHash']
 for row in origin['origins']:
  if row['file']=='launcher.mjs':
   for t in row['transforms']:
    if t['from']=='@SEP_GRAPH_HASH@':t['to']=graphHash
   row['resultSha256']=digest(root/'managed/bootstrap/launcher.mjs')
 origin['beta5Derivation']={'sourceOriginSha256':hashlib.sha256(raw).hexdigest(),'scope':'same fixed source/transforms; graph literal/result updated for reviewed memory bytes'}
 originPath.write_text(json.dumps(origin,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 manifestPath=root/'manifest.json';m=json.loads(manifestPath.read_bytes())
 for row in m['support']:
  if row['path']=='managed/bootstrap/ORIGIN.json':row['size']=originPath.stat().st_size;row['sha256']=digest(originPath)
 manifestPath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 # Independently verify updated origin by exact transform replay.
 row=next(x for x in origin['origins'] if x['file']=='launcher.mjs');source=repo/'tools/offline-upgrade-bridge-beta2/operator/shared/sep-update/runtime/launcher/launcher.mjs';b=source.read_bytes();assert hashlib.sha256(b).hexdigest()==row['sourceSha256']
 s=b.decode()
 for t in row['transforms']:
  assert s.count(t['from'])==t['count'];s=s.replace(t['from'],t['to'])
 assert s.encode()==(root/'managed/bootstrap/launcher.mjs').read_bytes()
 target=base/('DSH-SEP-'+label+'-0.2.1-beta.5-Windows-x64.zip')
 longRoot=Path('\\\\?\\'+str(root));files=sorted(p for p in longRoot.rglob('*') if p.is_file())
 with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
  for p in files:z.write(p,str(p.relative_to(longRoot)).replace('\\','/'))
 with zipfile.ZipFile(target)as z:assert z.testzip() is None;assert len(z.infolist())==len(files)
 assets.append({'name':target.name,'path':str(target),'size':target.stat().st_size,'sha256':digest(target),'kind':'installer'})
 print(json.dumps(assets[-1]),flush=True)
(stage/'INSTALLER-UPLOAD-PLAN-WINDOWS.json').write_text(json.dumps({'schema':1,'status':'pass','assets':assets},indent=2)+'\n',encoding='utf8')
spec={'schema':1,'expected':{'hostVersion':'0.2.1-rc.2','sepVersion':'0.2.1-beta.3-rc2-adapter.1','revision':'windows-package.rc2.1'},'archives':[{'kind':k,**{n:a[n] for n in ('path','size','sha256')}}for k,a in zip(['full','sep'],assets)],'outputRoot':str(base/'fresh-r1'),'python':str(Path(__import__('sys').executable)),'hostRoot':r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1\windows-packages-r1\official-donor','guardRecords':[]}
specPath=base/'INSTALL-SPEC.json';specPath.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
x=subprocess.run([str(node),str(repo/'tools/release-beta5/windows-verification/install-archives.mjs'),str(specPath)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3600)
(base/'install.stdout.log').write_bytes(x.stdout);(base/'install.stderr.log').write_bytes(x.stderr)
assert x.returncode==0,x.stdout[-3000:].decode(errors='replace')+x.stderr[-3000:].decode(errors='replace')
print('Full/Only ZIP extraction, audits, refusals, installation and runtime smoke passed',flush=True)

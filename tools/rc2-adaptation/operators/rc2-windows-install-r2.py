from pathlib import Path
import subprocess,json,hashlib
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');d=s/'source/tools/rc2-adaptation/windows-verification';origin=[]
for p in d.glob('*.py'):
 b=p.read_bytes();v=b.decode('utf-8');a=r'D:\AIData\ProjectWork\DSH\alpha2-windows-packages-20261015-r1';z=str(s/'windows-packages-r1')
 if a in v:
  n=v.count(a);p.write_text(v.replace(a,z),encoding='utf-8',newline='\n');origin.append({'path':p.name,'sourceSha256':hashlib.sha256(b).hexdigest(),'resultSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'from':a,'to':z,'count':n})
(d/'PYTHON-SCOPE-ORIGIN.json').write_text(json.dumps({'schema':1,'scope':'retain identical extraction policy; port hardcoded isolated work root only','transforms':origin},indent=2)+'\n',encoding='utf-8')
p=s/'windows-packages-r1/INSTALL-SPEC.json';v=json.loads(p.read_bytes());v['outputRoot']=str(s/'windows-packages-r1/fresh-install-r2');q=s/'windows-packages-r1/INSTALL-SPEC-r2.json';q.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
with (s/'evidence/windows-fresh-install-r2.log').open('xb') as f:p=subprocess.run(['node',str(d/'install-archives.mjs'),str(q)],stdout=f,stderr=f,timeout=2400)
print(json.dumps({'exit':p.returncode}));assert p.returncode==0

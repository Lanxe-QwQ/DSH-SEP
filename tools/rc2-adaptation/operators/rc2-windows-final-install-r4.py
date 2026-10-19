from pathlib import Path
import json,subprocess
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');P=S/'windows-packages-r1';v=json.loads((P/'INSTALL-SPEC.json').read_bytes());a=json.loads((P/'FINAL-ARCHIVES.json').read_bytes());assert a['status']=='pass'
v['archives']=[{k:r[k] for k in ['kind','path','size','sha256']} for r in a['archives']];v['outputRoot']=str(P/'fresh-final-r4')
spec=P/'INSTALL-SPEC-FINAL-r4.json'
with spec.open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.write('\n')
with (S/'evidence/windows-fresh-final-r4.log').open('xb') as log:
 r=subprocess.run(['node',str(S/'source/tools/rc2-adaptation/windows-verification/install-archives.mjs'),str(spec)],stdout=log,stderr=subprocess.STDOUT,timeout=2400)
print(json.dumps({'exit':r.returncode,'spec':str(spec)}));assert r.returncode==0

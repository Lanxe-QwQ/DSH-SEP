from pathlib import Path
import json,hashlib,subprocess
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');o=s/'windows-packages-r1';v=s/'source/tools/rc2-adaptation/windows-verification';source=o/'fresh-install-r3/RESULT.json';body=source.read_bytes();report=json.loads(body);assert report['status']=='pass';root=Path(report['installations'][0]['config']['releaseRoot']);p=v/'workspace-sources.json';old=p.read_bytes();data=json.loads(old)
for row in data['files']:
 row['path']=row['path'].replace('index-Dp57FHwW.js','index-CN7NIWNw.js');b=(root/row['path']).read_bytes();row['bytes']=len(b);row['sha256']=hashlib.sha256(b).hexdigest()
data['scope']='Actual installed RC.2 frontend/renderer/layout/sidebar source binding, retaining original DOM readiness requirements; not a product modification';data['officialCommit']='687f282e8625c6b8d11ff58211a90524be2e4317';data['historicalInputSha256']=hashlib.sha256(old).hexdigest();p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['headless-probe.mjs','default-desktop-probe.mjs']:
 p=v/name;b=p.read_text(encoding='utf-8');p.write_text(b.replace('Alpha.2','RC.2'),encoding='utf-8',newline='\n')
digest=hashlib.sha256(body).hexdigest()
for kind in ['full','sep']:
 with (s/'evidence'/('windows-installed-desktop-'+kind+'-r2.log')).open('xb') as log:r=subprocess.run(['node',str(v/'default-desktop-probe.mjs'),str(source),digest,kind,str(o/('desktop-'+kind+'-r2'))],stdout=log,stderr=log,timeout=1200)
 print(json.dumps({'kind':kind,'exit':r.returncode}),flush=True);assert r.returncode==0

from pathlib import Path
import json,hashlib,subprocess,time
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');o=s/'windows-packages-r1';v=s/'source/tools/rc2-adaptation/windows-verification';path=o/'fresh-install-r3/RESULT.json'
deadline=time.monotonic()+2400
while not path.exists():
 assert time.monotonic()<deadline;time.sleep(3)
body=path.read_bytes();result=json.loads(body);assert result['status']=='pass' and result['configurationsFrozen'];digest=hashlib.sha256(body).hexdigest()
def run(name,script,args,timeout=900):
 with (s/'evidence'/name).open('xb') as log:r=subprocess.run(['node',str(v/script),*map(str,args)],stdout=log,stderr=log,timeout=timeout)
 print(json.dumps({'step':name,'exit':r.returncode}),flush=True);assert r.returncode==0
run('windows-installed-host-r1.log','headless-probe.mjs',[path,digest,o/'headless-r1'],1200)
for kind in ['full','sep']:
 run('windows-installed-desktop-'+kind+'-r1.log','default-desktop-probe.mjs',[path,digest,kind,o/('desktop-'+kind+'-r1')],1200)
print(json.dumps({'status':'pass','scope':'actual Full/Only new installs, concurrent hosts and persistence reopen, two desktop rounds per package, no paid model calls'}))

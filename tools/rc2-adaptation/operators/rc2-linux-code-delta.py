from pathlib import Path
import subprocess,json
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1')
code=r"""from pathlib import Path
import json,hashlib
r=Path('/opt/dsh-sep-cross-platform/rc2-adaptation-20261018-r1');a=json.loads((r/'payload-r7/PAYLOAD-MANIFEST.json').read_bytes());b=json.loads((r/'payload-r8/PAYLOAD-MANIFEST.json').read_bytes());am={x['path']:x for x in a['entries']};bm={x['path']:x for x in b['entries']};added=sorted(set(bm)-set(am));removed=sorted(set(am)-set(bm));changed=sorted(p for p in am.keys()&bm.keys() if am[p]!=bm[p]);assert added==['RC2-PACKAGE-ORIGIN.json'] and removed==[] and changed==['README.md'];print(json.dumps({'schema':1,'status':'pass','sourceManifestSha256':hashlib.sha256((r/'payload-r7/PAYLOAD-MANIFEST.json').read_bytes()).hexdigest(),'deliveryManifestSha256':hashlib.sha256((r/'payload-r8/PAYLOAD-MANIFEST.json').read_bytes()).hexdigest(),'added':added,'removed':removed,'changed':changed,'runtimeCodeUnchanged':True,'scope':'exact complete entry records compared, including size/hash/mode/internal symlink targets; original Wayland program and archive-restored program execution code identical'}))
"""
r=subprocess.run(['wsl.exe','--distribution','DSH-SEP-Linux-RC','--user','sep-rc','--cd','/','--exec','/usr/bin/python3','-I','-B','-'],input=code.encode(),capture_output=True,timeout=90);assert r.returncode==0,r.stderr
value=json.loads(r.stdout);(s/'evidence/LINUX-CODE-DELTA.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');print(r.stdout.decode())

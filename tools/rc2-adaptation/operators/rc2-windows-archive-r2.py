from pathlib import Path
import zipfile,json,hashlib,re,subprocess
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');o=s/'windows-packages-r1';sha=lambda b:hashlib.sha256(b).hexdigest();archives=[];checks=[]
for kind,label in [('full','Full'),('sep','Only')]:
 root=o/('bundle-'+kind);m=json.loads((root/'manifest.json').read_bytes());entries=[('payload/'+r['path'],r) for r in m['payload']]+[(r['path'],r) for r in m['support']]+[(r['path'],r) for r in [m['graph'],m['descriptor']]]
 b=(root/'manifest.json').read_bytes();entries.append(('manifest.json',{'size':len(b),'sha256':sha(b)}));assert len({r[0] for r in entries})==len(entries)
 oldzip=zipfile.ZipFile(o/('DSH-SEP-'+label+'-Windows-x64-RC2-preview.zip'));oldnames=set(oldzip.namelist());missing=[p for p,r in entries if p not in oldnames];print(json.dumps({'kind':kind,'omitted':missing}),flush=True);assert len(missing)<=2 and all(p.endswith('.md') for p in missing)
 for rel in missing:
  b=Path('\\\\?\\'+str(root/rel)).read_bytes();v=b.decode('utf-8');assert not re.search(r'(C:[\\/]+Users[\\/]+PUBLIC_USER|sk-[A-Za-z0-9]{25,}|PUBLIC_ACCOUNT_ID)',v,re.I)
 archive=o/('DSH-SEP-'+label+'-Windows-x64-RC2-preview-r2.zip') if missing else o/('DSH-SEP-'+label+'-Windows-x64-RC2-preview.zip')
 if archive.exists():
  with zipfile.ZipFile(archive) as z:
   assert set(z.namelist())=={p for p,r in entries}
   for rel,row in entries:
    with z.open(rel) as f:
     h=hashlib.sha256();count=0
     while b:=f.read(1048576):h.update(b);count+=len(b)
    assert h.hexdigest()==row['sha256'] and count==row['size']
 else:
  with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
   for rel,row in entries:
    path=Path('\\\\?\\'+str(root/rel));st=path.stat();assert path.is_file() and st.st_nlink==1 and st.st_size==row['size'];h=hashlib.sha256();count=0;info=zipfile.ZipInfo(rel);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
    with path.open('rb') as f,z.open(info,'w',force_zip64=True) as q:
     while b:=f.read(1048576):h.update(b);count+=len(b);q.write(b)
    assert h.hexdigest()==row['sha256'] and count==row['size']
 h=hashlib.sha256()
 with archive.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 with zipfile.ZipFile(archive) as z:assert set(z.namelist())=={p for p,r in entries}
 archives.append({'kind':kind,'path':str(archive),'size':archive.stat().st_size,'sha256':h.hexdigest()});checks.append({'kind':kind,'expectedMembers':len(entries),'packedMembers':len(entries),'previousOmittedPaths':missing,'reason':'Python normal-path rglob silently omitted two long-path Markdown files; manifest-driven extended-path packing verifies every member','missingTextScan':'pass'})
(o/'ARCHIVES-r2.json').write_text(json.dumps({'schema':1,'status':'pass','archives':archives,'checks':checks},indent=2)+'\n',encoding='utf-8')
spec=json.loads((o/'INSTALL-SPEC.json').read_bytes());spec['archives']=archives;spec['outputRoot']=str(o/'fresh-install-r3');sp=o/'INSTALL-SPEC-r3.json';sp.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'packed','archives':archives}),flush=True)
with (s/'evidence/windows-fresh-install-r3.log').open('xb') as f:p=subprocess.run(['node',str(s/'source/tools/rc2-adaptation/windows-verification/install-archives.mjs'),str(sp)],stdout=f,stderr=f,timeout=2400)
print(json.dumps({'installExit':p.returncode}));assert p.returncode==0

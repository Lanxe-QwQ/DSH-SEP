from pathlib import Path
import json,hashlib,zipfile
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');o=s/'windows-packages-r1';program=o/'program';sha=lambda b:hashlib.sha256(b).hexdigest();js=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
g=json.loads((program/'graph.json').read_bytes());sealed=json.loads((o/'PROGRAM-SEALED.json').read_bytes());history=s/'evidence/windows-docs-history-r1';history.mkdir();components=json.loads((o/'support/docs/COMPONENTS.json').read_bytes());components['packages']=[]
for row in g['packages']:
 p=g['packagePaths'][row['id']];m=json.loads((program/p/'package.json').read_bytes());assert m['name']==row['name'] and m['version']==row['version'];components['packages'].append({'name':m['name'],'version':m['version'],'path':p,'declaredLicense':m.get('license')})
components['scope']='Current RC.2 graph packages and retained support runtime versions; not a full binary-internal SBOM';components['programGraphSha256']=sealed['graph']['sha256']
provenance={'schema':2,'hostVersion':'0.2.1-rc.2','sepVersion':'0.2.1-beta.3-rc2-adapter.1','revision':'windows-package.rc2.1','officialCommit':'687f282e8625c6b8d11ff58211a90524be2e4317','candidateSha256':'854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5','resultGraph':sealed['graph'],'resultDescriptor':sealed['descriptor'],'portabilityOriginSha256':sha((o/'PROGRAM-PORTABILITY.json').read_bytes()),'installerOriginSha256':sha((o/'INSTALLER-ORIGIN.json').read_bytes()),'officialSriProofSha256':sha((o/'OFFICIAL-SRI-PROOF.json').read_bytes()),'baselineRuntimeSource':'public Beta.3 Full, fixed captured module tree; official RC.2 source is separately pinned','privateInputImported':False,'dailySwitched':False,'releasePublished':False,'sourceStatus':'common adaptation was isolated source at build time; final external checkpoint binds the full source tree; hashes above bind actual shipped program'}
changed=[]
for name,value in [('COMPONENTS.json',components),('BUILD-PROVENANCE.json',provenance)]:
 before=(o/'support/docs'/name).read_bytes();(history/name).write_bytes(before);body=js(value).encode();changed.append({'path':'docs/'+name,'beforeSha256':sha(before),'resultSha256':sha(body)})
 for root in [o/'support',o/'bundle-full',o/'bundle-sep']:(root/'docs'/name).write_bytes(body)
archives=[]
for kind,label in [('full','Full'),('sep','Only')]:
 root=o/('bundle-'+kind);m=json.loads((root/'manifest.json').read_bytes())
 for row in m['support']:
  if row['path'] in [r['path'] for r in changed]:
   b=(root/row['path']).read_bytes();row['size']=len(b);row['sha256']=sha(b)
 (root/'manifest.json').write_text(js(m),encoding='utf-8')
 entries=[('payload/'+r['path'],r) for r in m['payload']]+[(r['path'],r) for r in m['support']]+[(r['path'],r) for r in [m['graph'],m['descriptor']]]
 b=(root/'manifest.json').read_bytes();entries.append(('manifest.json',{'size':len(b),'sha256':sha(b)}));assert len(set(p for p,r in entries))==len(entries)
 archive=o/('DSH-SEP-'+label+'-Windows-x64-RC2-preview-r3.zip')
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for rel,row in entries:
   p=Path('\\\\?\\'+str(root/rel));st=p.stat();assert p.is_file() and st.st_nlink==1 and st.st_size==row['size'];h=hashlib.sha256();count=0;info=zipfile.ZipInfo(rel);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   with p.open('rb') as f,z.open(info,'w',force_zip64=True) as q:
    while b:=f.read(1048576):h.update(b);count+=len(b);q.write(b)
   assert h.hexdigest()==row['sha256'] and count==row['size']
 h=hashlib.sha256()
 with archive.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 archives.append({'kind':kind,'path':str(archive),'size':archive.stat().st_size,'sha256':h.hexdigest(),'manifestSha256':sha((root/'manifest.json').read_bytes()),'members':len(entries)})
 print(json.dumps({'kind':kind,'archive':'pass','size':archive.stat().st_size}),flush=True)
(o/'FINAL-ARCHIVES.json').write_text(js({'schema':1,'status':'pass','archives':archives,'changesFromTestedR2':changed,'programGraphUnchanged':True,'installerCodeUnchanged':True,'scope':'two documentation files corrected to actual graph/package/provenance; support manifest hashes updated; every final archive member verified while packed','functionalEvidence':'fresh-install-r3 and associated actual installed Host/Desktop probes; same executable program graph; final archive installation separate'}),encoding='utf-8')

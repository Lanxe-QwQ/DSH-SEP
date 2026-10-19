from pathlib import Path
import hashlib,json,zipfile,os
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');E=S/'evidence';O=S/'source/tools/rc2-adaptation/macos/installer-validation';H=lambda b:hashlib.sha256(b).hexdigest();commit='fecf8489d4bc98e2cac515b2a705b861bda89b9d';run=39133136770
meta=json.loads((E/'mac-ci-r12-evidence/artifact.verified.json').read_bytes());reports=[json.loads((E/f'mac-ci-r12-parts/part-{i}/artifact.verified.json').read_bytes()) for i in range(1,5)]
def member(r,suffix):
 rows=[x for x in r['members'] if x['path']==suffix or x['path'].endswith('/'+suffix)];assert len(rows)==1,(suffix,len(rows));return rows[0]
def read(r,suffix):
 m=member(r,suffix);assert m['bytes']<=67108864
 with zipfile.ZipFile(r['path']) as z:b=z.read(m['path'])
 assert len(b)==m['bytes'] and H(b)==m['sha256'];return json.loads(b),m,b
r,rr,rb=read(meta,'installer/RESULT.json');inv,ir,ib=read(meta,'installer/PACKAGE-INVENTORY.json');guard,gr,gb=read(meta,'namespace-guard/RESULT.json');port,_,_=read(meta,'INSTALLER-NAMESPACE-ORIGIN.json');build,_,_=read(meta,'REPAIRED-INSTALLER-BUILD-ORIGIN.json');parts,_,pb=read(reports[0],'PARTS.json')
assert r['status']==guard['status']==parts['status']=='pass';assert r['sourceCommit']==parts['sourceCommit']==commit;assert len(guard['completed'])==3 and all(x['status']=='pass' for x in guard['completed']) and guard['cleanup']['status']=='pass';assert guard['completed'][2]['code']=='SEP_INSTALLER_DATA_EXISTS' and guard['completed'][2]['governanceCreated'] is False and guard['completed'][2]['targetCreated'] is False and guard['completed'][2]['sentinelUnchanged'] is True
assert build['guardResultSha256']==H(gb) and len(port['changes'])==2 and [x['count'] for x in port['changes']]==[2,1]
assert parts['sha256']==r['artifactSha256'] and parts['bytes']==r['artifactBytes'] and parts['artifact']==r['artifact'] and len(parts['parts'])==4
assert r['treeSha256']==inv['treeSha256'] and r['payloadUnchanged'] is True and r['nativeSourceUnchanged'] is True
source=json.loads((O/'installer-sources.json').read_bytes());by={x['path']:x for x in source['files']}
for group,kind in [(r['resources']['source']['runtime'],'production-runtime'),(r['resources']['source']['native'],'production-helper'),(r['nativeInputs'],'production-native')]:
 assert len(group)==len([x for x in by.values() if x['kind']==kind])
 for x in group:assert by[x['path']]['kind']==kind and by[x['path']]['sha256']==x['sha256']
pins=json.loads((O/'installer-pins.json').read_bytes());payload=pins['payload'];assert r['payload']==dict(sourceAssemblySha256=payload['assemblySha256'],programSha256=payload['programSha256'],bootstrapSha256=payload['bootstrapSha256'],archiveSha256=payload['archiveSha256'],treeSha256=payload['treeSha256'],entries=payload['entries'],totalBytes=payload['totalBytes'])
current=next(x for x in guard['helpers'] if Path(x['path']).name=='rc2-account');assert current['sourceSha256']==by['installer-entry/account-native.c']['sha256']
out=S/'artifacts/macos-r12';out.mkdir(exist_ok=False);archive=out/r['artifact'];whole=hashlib.sha256();total=0
with archive.open('xb') as dst:
 for i,q in enumerate(reports,1):
  part=parts['parts'][i-1];assert part['index']==i;other,_,ob=read(q,'PARTS.json');assert ob==pb
  m=member(q,part['path']);assert m['bytes']==part['bytes'] and m['sha256']==part['sha256'];h=hashlib.sha256();n=0
  with zipfile.ZipFile(q['path']) as z,z.open(m['path']) as f:
   for b in iter(lambda:f.read(1048576),b''):n+=len(b);total+=len(b);h.update(b);whole.update(b);dst.write(b)
  assert n==part['bytes'] and h.hexdigest()==part['sha256']
 dst.flush();os.fsync(dst.fileno())
assert total==r['artifactBytes'] and whole.hexdigest()==r['artifactSha256']
for n in ['installer-pins.json','installer-transport-pins.json']:
 with (E/('before-r12-'+n)).open('xb') as f:f.write((O/n).read_bytes())
pins['installer']=dict(status='ready',commit=commit,artifact=r['artifact'],assemblySha256=H(rb),assemblyBytes=len(rb),archiveSha256=r['artifactSha256'],archiveBytes=r['artifactBytes'],inventorySha256=H(ib),inventoryBytes=len(ib),treeSha256=r['treeSha256'],manifestSha256=r['manifestSha256'],payload=r['payload'],nativeInputs=r['nativeInputs'],runtimeInputs=r['resources']['source']['runtime'],helperInputs=r['resources']['source']['native'])
def tr(q,name):return dict(id=q['artifactId'],name=name,bytes=q['bytes'],sha256=q['sha256'],members=q['members'])
transport=json.loads((O/'installer-transport-pins.json').read_bytes());transport['installer']=dict(status='ready',sourceCommit=commit,runId=run,artifacts=[tr(meta,f'sep-rc2-macos-repaired-evidence-{run}')]+[tr(q,f'sep-rc2-macos-repaired-part-{i}-{run}') for i,q in enumerate(reports,1)],outputs=[dict(name=n,artifactId=meta['artifactId'],member=m['path']) for n,m in [('RESULT.json',rr),('PACKAGE-INVENTORY.json',ir)]],parts=[dict(index=i,artifactId=q['artifactId'],member=member(q,p['path'])['path'],bytes=p['bytes'],sha256=p['sha256']) for i,(q,p) in enumerate(zip(reports,parts['parts']),1)])
for n,v in [('installer-pins.json',pins),('installer-transport-pins.json',transport)]:
 (O/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
proof=dict(schema=1,status='pass',scope='independent repaired archive and native-guard/source/payload review; new full installation still pending',sourceCommit=commit,runId=run,artifact=str(archive),bytes=total,sha256=r['artifactSha256'],applicationUnchanged=True,nativeGuardChecks=3,sourceChanges=3,metadataArtifact=meta['artifactId'],parts=[q['artifactId'] for q in reports],sourceManifestSha256=H((O/'installer-sources.json').read_bytes()))
with (E/'MAC-REPAIRED-INSTALLER-PIN-REVIEW.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps(proof))

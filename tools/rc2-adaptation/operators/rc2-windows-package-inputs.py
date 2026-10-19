from pathlib import Path
import json,hashlib,shutil,re
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');out=s/'windows-packages-r1';out.mkdir();src=s/'windows-runtime-r3';program=out/'program';program.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
graph=json.loads((src/'graph.json').read_bytes());assert len(graph['files'])>20000
for row in graph['files']:
 p=src/row['path'];body=p.read_bytes();assert sha(body)==row['sha256'];q=program/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(body)
(out/'BASE-GRAPH.json').write_bytes((src/'graph.json').read_bytes())
changes=[];prefix=src.as_uri()+'/node_modules/dsh-sep-bundle/'
for p in sorted((program/'daily-adapter').glob('*.js')):
 b=p.read_bytes();v=b.decode();n=v.count(prefix);v=v.replace(prefix,'../node_modules/dsh-sep-bundle/');assert 'file://' not in v;assert not re.search(r'[A-Z]:[\\/]AIData',v);p.write_bytes(v.encode());changes.append({'path':p.relative_to(program).as_posix(),'sourceSha256':sha(b),'resultSha256':sha(v.encode()),'coreImportReplacements':n})
# Keep full private origins in this stage, replace public package origins by
# hashes and declared transformations. The immutable tested r3 is not edited.
for rel in ['daily-adapter/ORIGIN.json','node_modules/@deepseek-ai/dsh-recovery/DAILY-ORIGIN.json']:
 p=program/rel;b=p.read_bytes();value=json.loads(b)
 if rel.startswith('daily-adapter'):
  value={'schema':1,'kind':'RC.2 portable daily adapter','historicalOriginSha256':sha(b),'sourceGraphSha256':sha((src/'graph.json').read_bytes()),'files':changes}
 else:value['coreRoot']='../../dsh-sep-bundle';value['privateOriginSha256']=sha(b)
 p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');changes.append({'path':rel,'sourceSha256':sha(b),'resultSha256':sha(p.read_bytes()),'reason':'public hash-bound origin; original stage record retained'})
prefixes=[str(s).replace('\\','/')+'/desktop-source/',str(s).replace('\\','/')+'/official-source/',str(s).replace('\\','/')+'/host-rc2/',str(s).replace('\\','/')+'/source/']
for p in sorted(program.rglob('*')):
 if not p.is_file() or p.suffix not in ['.js','.mjs','.cjs','.json','.yaml','.yml','.html','.css','.md']:continue
 b=p.read_bytes()
 try:v=b.decode('utf-8')
 except UnicodeDecodeError:continue
 if not re.search(r'[A-Z]:[\\/]AIData[\\/]ProjectWork[\\/]DSH',v,re.I):continue
 if p.suffix=='.json':
  # No private effective input was used. Existing source origin files inside
  # the fixed public candidate are not rewritten silently.
  if str(s) in v or str(s).replace('\\','/') in v:
   raise AssertionError('UNCLASSIFIED_LOCAL_ORIGIN: '+str(p.relative_to(program)))
  continue
 lines=v.splitlines(keepends=True);n=0
 for i,line in enumerate(lines):
  if not re.search(r'[A-Z]:[\\/]AIData[\\/]ProjectWork[\\/]DSH',line,re.I):continue
  assert re.match(r'^\s*(?://|/\*|\*|"[^"\r\n]+"\([^\r\n]*\)\s*\{)',line),'NON_LABEL_PATH: '+str(p.relative_to(program))
  normalized=line.replace('\\\\','/').replace('\\','/')
  for prefix_ in prefixes:
   if prefix_ in normalized:n+=normalized.count(prefix_);normalized=normalized.replace(prefix_,'sep-build/')
  assert not re.search(r'[A-Z]:[\\/]AIData[\\/]ProjectWork[\\/]DSH',normalized,re.I),'UNCLASSIFIED_LABEL: '+str(p.relative_to(program))
  lines[i]=normalized
 result=''.join(lines)
 if result!=v:p.write_bytes(result.encode());changes.append({'path':p.relative_to(program).as_posix(),'sourceSha256':sha(b),'resultSha256':sha(result.encode()),'reason':'non-functional compiler label redaction','count':n})
(out/'PROGRAM-PORTABILITY.json').write_text(json.dumps({'schema':1,'status':'pass','changes':changes,'originalProgramUnchanged':True},indent=2)+'\n',encoding='utf-8')
support=out/'support';old=Path(r'D:\AIData\ProjectWork\DSH\alpha2-windows-packages-20261015-r1/support');shutil.copytree(old,support,ignore=lambda d,n:{x for x in n if Path(d)==old/'runtime' and x=='office-skills'})
shutil.copytree(s/'official-source/packages/skill/skill-office/assets',support/'runtime/office-skills')
installer=s/'source/tools/alpha2-windows/installer';records=[]
for name in ['install.mjs','fresh-profile.mjs','daily-profile.mjs']:
 b=(installer/name).read_bytes();v=b.decode();edits=[]
 for a,z in [('0.2.1-alpha.2','0.2.1-rc.2'),('0.2.1-beta.3-alpha2-adapter.1','0.2.1-beta.3-rc2-adapter.1'),('windows-package.2','windows-package.rc2.1')]:
  n=v.count(a)
  if n:v=v.replace(a,z);edits.append({'from':a,'to':z,'count':n})
 if name=='fresh-profile.mjs':
  a="await save(join(profileRoot,'cordis.patch.yml'),converted.patches);";assert v.count(a)==1
  z="const {createRequire}=await import('node:module');const {pathToFileURL}=await import('node:url');const require=createRequire(join(program,'package.json'));const {loadOverlayPatches}=await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-app-boot')));const nativeRows=['standard','cordis','minimal','ptc'].map(name=>loadOverlayPatches('dsh',join(program,'node_modules/@deepseek-ai/dsh-web-app/presets',name+'.patch.yml'))[0].insert[0]);await save(join(profileRoot,'cordis.patch.yml'),[...adaptDailyPresets(nativeRows),...converted.patches]);"
  v=v.replace(a,z);v="import {adaptDailyPresets} from './daily-presets.mjs';\n"+v;edits.append({'from':a,'to':z,'count':1})
 p=support/'installer'/name;p.write_text(v,encoding='utf-8',newline='\n');records.append({'file':name,'sourceSha256':sha(b),'resultSha256':sha(v.encode()),'transforms':edits})
shutil.copyfile(s/'source/tools/rc2-adaptation/runtime/daily-presets.mjs',support/'installer/daily-presets.mjs')
(out/'INSTALLER-ORIGIN.json').write_text(json.dumps({'schema':1,'records':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'prepared','programFiles':len(graph['files']),'changes':len(changes),'support':str(support)}))

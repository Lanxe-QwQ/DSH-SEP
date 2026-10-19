from pathlib import Path
import json,hashlib,zipfile
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');src=s/'source/tools/rc2-adaptation';sha=lambda b:hashlib.sha256(b).hexdigest();js=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
merge=json.loads((s/'evidence/DESKTOP-MERGE.json').read_bytes());paths={x['path'] for x in merge['files']}
for name in ['integrated-desktop-r2','integrated-client-r3']:
 v=json.loads((s/name/'BUILD-INPUTS.json').read_bytes());inputs=v.get('inputs',{})
 if isinstance(inputs,dict):
  for p,h in inputs.items():
   q=Path(p)
   if q.is_relative_to(s/'desktop-source'):paths.add(q.relative_to(s/'desktop-source').as_posix())
capture=src/'desktop-source-overlay.zip';rows=[]
with zipfile.ZipFile(capture,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel in sorted(paths):
  p=s/'desktop-source'/rel
  if not p.is_file():continue
  b=p.read_bytes();z.writestr(rel,b);u=s/'official-source'/rel;rows.append({'path':rel,'size':len(b),'sha256':sha(b),'officialSha256':sha(u.read_bytes()) if u.is_file() else None})
(src/'DESKTOP-SOURCE-CAPTURE.json').write_text(js({'schema':1,'scope':'exact desktop overlay and local desktop-source compiler inputs; reconstruct on official RC.2 source, then apply declared build operators. No daily data, caches or node_modules included','officialVersion':'0.2.1-rc.2','officialCommit':'687f282e8625c6b8d11ff58211a90524be2e4317','archiveSha256':sha(capture.read_bytes()),'files':rows,'mergeReceiptSha256':sha((s/'evidence/DESKTOP-MERGE.json').read_bytes()),'desktopBuildInputsSha256':sha((s/'integrated-desktop-r2/BUILD-INPUTS.json').read_bytes()),'clientBuildInputsSha256':sha((s/'integrated-client-r3/BUILD-INPUTS.json').read_bytes())}),encoding='utf-8')
# The tested archives and final archives differ only in two documentation rows.
o=s/'windows-packages-r1';old=json.loads((o/'ARCHIVES-r2.json').read_bytes());new=json.loads((o/'FINAL-ARCHIVES.json').read_bytes());deltas=[]
for n in new['archives']:
 a=next(x for x in old['archives'] if x['kind']==n['kind'])
 with zipfile.ZipFile(a['path']) as z:before=json.loads(z.read('manifest.json'));oldNames=set(z.namelist())
 with zipfile.ZipFile(n['path']) as z:after=json.loads(z.read('manifest.json'));newNames=set(z.namelist())
 assert oldNames==newNames and before['payload']==after['payload'] and before['required']==after['required'] and before['graph']==after['graph'] and before['descriptor']==after['descriptor'] and before['desktop']==after['desktop']
 bm={r['path']:r for r in before['support']};am={r['path']:r for r in after['support']};assert bm.keys()==am.keys();changed=[p for p in bm if bm[p]!=am[p]];assert set(changed)=={'docs/COMPONENTS.json','docs/BUILD-PROVENANCE.json'}
 deltas.append({'kind':n['kind'],'status':'pass','testedArchiveSha256':a['sha256'],'finalArchiveSha256':n['sha256'],'changedSupport':changed,'allExecutableAndInstallerFilesUnchanged':True,'finalMembers':len(newNames)})
(s/'evidence/WINDOWS-FINAL-DELTA.json').write_text(js({'schema':1,'status':'pass','scope':'manifest and entry-set comparison; final member content hashes were independently verified while packing; runtime tests target identical executable graphs','deltas':deltas}),encoding='utf-8')
desktop=[]
for kind in ['full','sep']:
 p=o/('desktop-'+kind+'-r2/RESULT.json');r=json.loads(p.read_bytes());assert r['status']=='blocked' and r['coreStatus']=='pass';assert len(r['rounds'])==2 and all(t['status']=='pass' for t in r['rounds']);desktop.append({'kind':kind,'status':'blocked','coreStatus':'pass','rounds':2,'resultSha256':sha(p.read_bytes()),'blockedScope':'direct unsigned start.ps1 under existing execution policy; standard VBS and exact launcher desktop flow recorded separately','notVerified':r['notVerified']})
(s/'evidence/WINDOWS-CURRENT.json').write_text(js({'schema':1,'host':'0.2.1-rc.2','sep':'0.2.1-beta.3-rc2-adapter.1','freshInstall':{'status':'pass','resultSha256':sha((o/'fresh-install-r3/RESULT.json').read_bytes()),'scope':'both actual archives; hash coverage, original donor unchanged, refusal guards, runtime smoke; final delta is documentation only'},'managedHost':{'status':'pass','resultSha256':sha((o/'headless-r1/RESULT.json').read_bytes()),'scope':'two simultaneous independent hosts, ledger/settings isolation, cold reopen, all tracked host exits and P2 locks confirmed'},'desktop':desktop,'finalArchiveDelta':'WINDOWS-FINAL-DELTA.json','privacy':{'status':'pass','recordSha256':sha((o/'PRIVACY-SCAN.json').read_bytes()),'longPathMissingFiles':'two public Markdown descriptions separately scanned in corrected packing; original omission retained'},'duplicateProbe':{'code':'EEXIST','applicationLaunched':False,'scope':'one accidental duplicate probe was refused before starting; its redirected console log overlapped the original Only console log, while per-round source logs and final RESULT remained intact'},'dailySwitched':False,'releasePublished':False}),encoding='utf-8')
print(js({'desktopSourceFiles':len(rows),'desktopSourceZipSha256':sha(capture.read_bytes()),'windowsDelta':deltas}))

from pathlib import Path
import subprocess,json,hashlib,os,re
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');R=S/'source';out=S/'source-checkpoint-final'
assert not out.exists();out.mkdir()
env=os.environ.copy();env.update(GIT_CONFIG_NOSYSTEM='1')
def git(*args,cwd=R,check=True):
 p=subprocess.run(['git',*args],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
 return p.stdout
def put(p,v):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert json.loads((S/'evidence/FINAL-VERIFICATION.json').read_bytes())['status']=='pass'
state=git('status','--porcelain=v1','-z').decode('utf-8').split('\0')
for row in filter(None,state):
 path=row[3:];assert path=='README.md' or path.startswith('tools/rc2-adaptation/'),row
git('add','--','README.md','tools/rc2-adaptation')
staged=git('diff','--cached','--name-only','-z').decode().split('\0');assert len(staged)>10
assert all(p=='README.md' or p.startswith('tools/rc2-adaptation/') for p in staged if p)
wsargs=['-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check']
ws=subprocess.run(['git',*wsargs],cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
assert ws.returncode in (0,2)
(out/'WHITESPACE-RAW.log').open('xb').write(ws.stdout)
findings=re.findall(r'^(tools/[^\n:]+):[0-9]+: ',ws.stdout.decode('utf-8'),re.M)
frozen=json.loads((R/'tools/rc2-adaptation/CANDIDATE-SOURCE.json').read_bytes())
pins={x['path']:x['sha256'] for x in frozen['files']}
for path in findings:
 assert path.startswith('tools/rc2-adaptation/candidate/'),path
 relative=path.removeprefix('tools/rc2-adaptation/candidate/')
 assert sha(R/path)==pins[relative],path
git(*wsargs,'--','.',':(exclude)tools/rc2-adaptation/candidate')
put(out/'WHITESPACE-REVIEW.json',dict(status='pass',scope='current adaptation changes excluding byte-fixed already-tested runtime capture; full raw check retains inherited whitespace findings',fullCheckExit=ws.returncode,frozenCaptureFindingCount=len(findings),frozenCaptureFiles=sorted(set(findings)),nonCaptureCheck='pass',lineEndings='CRLF recognized per command; no global Git config or input bytes changed'))
commit=git('-c','user.name=Codex','-c','user.email=codex@users.noreply.github.com','commit','-m','feat: seal isolated DSH RC2 adaptation and platform preview evidence').decode()
head=git('rev-parse','HEAD').decode().strip();assert not git('status','--porcelain=v1').strip()
branch=git('branch','--show-current').decode().strip();assert branch=='codex/sep-rc2-adaptation-20261018'
bundle=out/'DSH-SEP-RC2-adaptation-source.bundle';git('bundle','create',str(bundle),branch);git('bundle','verify',str(bundle))
restored=out/'restored';git('-c','core.autocrlf=true','clone','--no-hardlinks','--branch',branch,str(bundle),str(restored))
assert git('rev-parse','HEAD',cwd=restored).decode().strip()==head
assert not git('status','--porcelain=v1',cwd=restored).strip()
git('fsck','--full',cwd=restored)
paths=[x.decode('utf-8') for x in git('ls-files','-z').split(b'\0') if x]
rows=[]
for path in paths:
 p=R/path;q=restored/path
 assert p.is_file() and q.is_file(),path
 a=sha(p);assert sha(q)==a,path
 rows.append(dict(path=path,bytes=p.stat().st_size,sha256=a))
record=dict(schema=1,status='pass',source=str(R),sourceCommit=head,restoredCommit=head,branch=branch,bundle=str(bundle),bundleBytes=bundle.stat().st_size,bundleSha256=sha(bundle),restored=str(restored),verifiedFiles=len(rows),gitFsck='pass',workingTree='clean',scope='all tracked source bytes restored and compared; not a new runtime test or public release',files=rows)
put(out/'RESTORE-VERIFIED.json',record)
put(out/'CHECKPOINT.json',{k:v for k,v in record.items() if k!='files'})
print(json.dumps({k:v for k,v in record.items() if k!='files'},ensure_ascii=False))

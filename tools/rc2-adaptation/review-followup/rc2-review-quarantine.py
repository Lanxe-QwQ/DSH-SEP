from pathlib import Path
import hashlib,json,os,stat,tarfile,shutil
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');A=S/'artifacts'
N='dsh-sep-bundle-0.2.1-beta.3-rc2-adapter.1.tgz'
OLD='f80533561f1c91beab7656f014fa56e05936489a94224cd1f9913766416c8ca8'
NOW='854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5'
old=A/N;current=A/'r4'/N;dest=A/'history/pre-r4'/N
H=lambda b:hashlib.sha256(b).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
assert A.resolve()==A and old.resolve()==old and current.resolve()==current
assert old.is_relative_to(S) and dest.is_relative_to(S) and old!=dest
before=old.stat();assert stat.S_ISREG(before.st_mode) and before.st_nlink==1
assert H(old.read_bytes())==OLD and H(current.read_bytes())==NOW
def members(p):
 with tarfile.open(p) as t:
  rows=[(m.name,H(t.extractfile(m).read())) for m in t.getmembers() if m.isfile()]
  assert len(rows)==len(dict(rows));return dict(rows)
x=members(old);y=members(current);different=[p for p in sorted(x.keys()|y.keys()) if x.get(p)!=y.get(p)]
assert len(different)==4
dest.parent.mkdir(parents=True,exist_ok=False);assert dest.parent.resolve()==dest.parent
with old.open('rb') as source,dest.open('xb') as out:
 assert os.fstat(source.fileno()).st_ino==before.st_ino
 shutil.copyfileobj(source,out);out.flush();os.fsync(out.fileno())
assert H(dest.read_bytes())==OLD and H(old.read_bytes())==OLD
after=old.stat();assert (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)==(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
row=dict(schema=1,status='superseded',installAllowed=False,originalPath=str(old),path=str(dest),sha256=OLD,bytes=before.st_size,currentPath='r4/'+N,currentSha256=NOW,differentBodyMembers=different,scope='historical unreviewed pre-r4 candidate; current reviewed security bridge differs',copyVerifiedBeforeOriginalRemoval=True,usageReview='current builders, Mac pins, Linux input capture and CONTINUATION explicitly select r4 or embedded pinned copy; historical traces retain original paths',historicalLogsRewritten=False)
save(dest.parent/'SUPERSEDED.json',row)
# Remove exactly this verified historical duplicate from the misleading root.
# This is neither recursive deletion nor deletion of the retained original bytes.
old.unlink();assert not old.exists() and H(dest.read_bytes())==OLD
save(A/(N+'.SUPERSEDED.json'),row)
pointer=dict(schema=1,status='ready',readinessScope='current exact candidate input only; not a public Release or daily-install approval',publicInstallable=False,path='r4/'+N,sha256=NOW,bytes=current.stat().st_size,obsoleteRootName=N,historical='history/pre-r4/SUPERSEDED.json')
save(A/'CURRENT-CANDIDATE.json',pointer)
with (A/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write('# 当前与历史候选\n\n当前套件输入仅取 CURRENT-CANDIDATE.json 所指的 r4 包并校验 SHA-256。\n原顶层同名 tgz 已复制核验后归档至 history/pre-r4，禁止安装。\n文件名和版本号相同不代表字节相同；旧日志原样保留，历史路径由 SUPERSEDED.json 对账。\n本索引不代表批准日常切换或公开发布。\n')
save(S/'source/tools/rc2-adaptation/review-followup/ARTIFACT-DISPOSITION.json',dict(current=pointer,historical=row))
print(json.dumps(dict(status='quarantined',historicalSha256=OLD,currentSha256=NOW,differentBodyMembers=different)))

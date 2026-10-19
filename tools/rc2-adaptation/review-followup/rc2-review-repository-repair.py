from pathlib import Path
import hashlib,json,re
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');R=S/'source';O=R/'tools/rc2-adaptation/review-followup'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
changes=[]
def edit(path,transform):
 p=R/path;before=p.read_bytes();newline='\r\n' if b'\r\n' in before else '\n'
 text=before.decode('utf-8').replace('\r\n','\n');after=transform(text).replace('\n',newline).encode('utf-8')
 assert after!=before;p.write_bytes(after)
 changes.append(dict(path=path,sourceSha256=H(before),resultSha256=H(after),lineEndingPreserved=newline))
def replace_owner(text):
 assert 'Lance-QwQ/DSH-SEP' in text
 return text.replace('Lance-QwQ/DSH-SEP','Lanxe-QwQ/DSH-SEP')
for path in ['package.json','README.md','.github/workflows/sep-release-relay.yml']:edit(path,replace_owner)
function='''          def adapt_repository_source(name,data):
              if name!='relay.py':return data
              assert hashlib.sha256(data).hexdigest()=='66440f56b84d4cc7d8388601721b64412845989f5e6c56aa81da8482a6350829'
              old=b"REPO='Lance-QwQ/DSH-SEP';API="
              new=b"REPO='Lanxe-QwQ/DSH-SEP';API="
              assert data.count(old)==1
              derived=data.replace(old,new)
              assert hashlib.sha256(derived).hexdigest()=='d5f7715f57a640b1f66912f67b6f3f075d073db055ef3617e09fced529fa68b9'
              return derived
          assert os.environ['GITHUB_REPOSITORY']=='Lanxe-QwQ/DSH-SEP' and os.environ['GITHUB_REF']=='refs/heads/main'
'''
def beta2(text):
 assert text.count('Lance-QwQ/DSH-SEP')==2
 text=replace_owner(text)
 anchor="          c=os.environ['EXPECTED_COMMIT'];"
 assert text.count(anchor)==1;text=text.replace(anchor,function+anchor)
 anchor='              (root/name).write_bytes(data)'
 assert text.count(anchor)==1
 return text.replace(anchor,"              (root/name).write_bytes(adapt_repository_source(name,data))\n              if name=='relay.py':print(json.dumps({'adaptation':'repository-owner','sourceSha256':expected,'resultSha256':hashlib.sha256((root/name).read_bytes()).hexdigest()}),flush=True)")
edit('.github/workflows/sep-beta2-release-relay.yml',beta2)
save(O/'REPOSITORY-RENAME.json',dict(schema=1,scope='local source repair only; no dispatch, upload or Release action',repository='Lanxe-QwQ/DSH-SEP',changes=changes,frozenBeta2Relay=dict(sourceSha256='66440f56b84d4cc7d8388601721b64412845989f5e6c56aa81da8482a6350829',resultSha256='d5f7715f57a640b1f66912f67b6f3f075d073db055ef3617e09fced529fa68b9',replacementCount=1,historicalReleaseFilesUnchanged=True),manualMainOnly=True,remoteWorkflowDispatch='not_run'))
p=R/'tools/rc2-adaptation/macos/runtime-helper.mjs';raw=p.read_bytes()
assert H(raw)=='261a337751be3e2f0f706b267cbb7bde5509a68c436b6f202ca39b2146ace4c2'
text=raw.decode('utf-8');comments=re.findall(r'^// D:/[^\r\n]+',text,re.M);labels=re.findall(r'^\s+"D:/[^"\r\n]+"\(exports, module\)',text,re.M)
assert comments and labels
save(O/'GENERATED-PATHS.json',dict(schema=1,disposition='retained-frozen-generated-input',path='tools/rc2-adaptation/macos/runtime-helper.mjs',sha256=H(raw),moduleIdsAlsoContainPaths=True,commentLabels=len(comments),moduleFactoryLabels=len(labels),rebuilt=False,candidateAndPackagesChanged=False,classification='nonsecret local build-stage labels; generated module keys as well as comments',notClaimed='no exhaustive privacy/taint certification',futureBuildRequirement='Generate with controlled relative source roots and new input/output pins; native revalidation before replacing the fixed helper. Removing comments alone is insufficient.',oneShotOperators='retained as documented lab tooling, not product installation entries'))
print(json.dumps(dict(status='prepared',sourceFilesChanged=len(changes),generatedHelperByteUnchanged=True,comments=len(comments),moduleLabels=len(labels))))

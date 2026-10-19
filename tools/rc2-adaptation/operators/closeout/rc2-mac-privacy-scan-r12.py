from pathlib import Path,PurePosixPath
import hashlib,json,re,stat,zipfile
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');p=S/'artifacts/macos-r12/DSH-SEP-macOS-RC2-installer-preview.zip';expected='1c3a62ae966fe21b58e9ee6a63841cd5e9a30b8415e292b5008dec03b9941a77'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
before=p.stat();assert before.st_nlink==1 and p.resolve()==p and before.st_size==862171913 and digest(p)==expected
patterns={
 'known-personal-Windows-home':re.compile(rb'C:(?:[/\\]){1,4}Users(?:[/\\]){1,4}(?:PUBLIC_USER|Administrator)(?:[/\\])',re.I),
 'private-key-header':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'provider-token-like':re.compile(rb'(?<![A-Za-z0-9])sk-(?:proj-|ant-|or-v1-)?[A-Za-z0-9_-]{20,}'),
 'github-token-like':re.compile(rb'(?<![A-Za-z0-9])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})')}
hits=[];names=[];seen=set();files=0;total=0
with zipfile.ZipFile(p) as z:
 assert len(z.namelist())==len(set(z.namelist()))
 for info in z.infolist():
  path=PurePosixPath(info.filename);assert not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
  if info.is_dir():continue
  files+=1;assert info.file_size<=2147483648;total+=info.file_size;assert total<=8589934592
  name=path.name.lower()
  if name in {'.env','id_rsa','id_ed25519','credentials.json','auth.json','secrets.json','budget-ledger.json','ledger.json','session.json','session.v3.jsonl','session.v4.jsonl'}:names.append({'entry':info.filename,'category':'possible-private-runtime-or-credential-name','bytes':info.file_size})
  n=0;tail=b''
  with z.open(info) as f:
   while True:
    chunk=f.read(1024*1024)
    if not chunk:break
    data=tail+chunk;base=n-len(tail)
    for label,pattern in patterns.items():
     for match in pattern.finditer(data):
      key=(info.filename,label,base+match.start())
      if key not in seen:
       seen.add(key);hits.append(dict(entry=info.filename,pattern=label,offset=key[2],matchSha256=hashlib.sha256(match[0]).hexdigest()));assert len(hits)<=10000
    n+=len(chunk);tail=data[-4096:]
  assert n==info.file_size
after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and digest(p)==expected
r=dict(schema=1,status='pass' if not hits and not names else 'blocked',archive=str(p),sha256=expected,bytes=before.st_size,filesScanned=files,uncompressedBytesScanned=total,scope='read-only ASCII byte signatures across every archive file including ASAR/native bytes, plus defined private filename checks; no decryption or exhaustive semantic/binary privacy audit',patterns=list(patterns),findings=hits,filenameFindings=names,comprehensivePrivacyAudit=False,archiveUnchanged=True)
with (S/'evidence/MAC-PRIVACY-SCAN-r12.json').open('x',encoding='utf8') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:r[k] for k in ['status','filesScanned','uncompressedBytesScanned','findings','filenameFindings','comprehensivePrivacyAudit']}))

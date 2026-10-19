from pathlib import Path
import hashlib,tarfile,subprocess,json
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1')
name='dsh-sep-bundle-0.2.1-beta.3-rc2-adapter.1.tgz'
a=S/'artifacts'/name;b=S/'artifacts/r4'/name
H=lambda x:hashlib.sha256(x).hexdigest()
def members(p):
 with tarfile.open(p) as t:return {m.name:H(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}
x=members(a);y=members(b)
r=S/'source';raw=subprocess.check_output(['git','show','HEAD:release/v0.2.1-beta.2/relay.py'],cwd=r)
old=b"REPO='Lance-QwQ/DSH-SEP';API=";new=b"REPO='Lanxe-QwQ/DSH-SEP';API="
assert raw.count(old)==1
print(json.dumps(dict(oldSize=a.stat().st_size,oldSha256=H(a.read_bytes()),currentSize=b.stat().st_size,currentSha256=H(b.read_bytes()),differentMembers=[p for p in sorted(x.keys()|y.keys()) if x.get(p)!=y.get(p)],relaySourceSha256=H(raw),relayCurrentOwnerSha256=H(raw.replace(old,new))),indent=2))

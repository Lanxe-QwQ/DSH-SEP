from pathlib import Path
import hashlib,json
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1')
O=S/'source/tools/rc2-adaptation';target=O/'candidate';target.mkdir(exist_ok=False)
rows=[]
for p in sorted((S/'candidate-source').rglob('*')):
 if not p.is_file():continue
 r=p.relative_to(S/'candidate-source');b=p.read_bytes();q=target/r;q.parent.mkdir(exist_ok=True,parents=True);q.write_bytes(b)
 assert q.read_bytes()==b
 rows.append(dict(path=r.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
assert len(rows)==445
(O/'.gitattributes').write_text('* -text !eol\n',encoding='utf8',newline='\n')
(O/'macos/.gitattributes').write_text('* -text !eol\n',encoding='utf8',newline='\n')
(O/'CANDIDATE-SOURCE.json').write_text(json.dumps(dict(schema=1,status='pass',scope='exact tested 445-file unpacked runtime; source copy verification, not new runtime execution',host='0.2.1-rc.2',version='0.2.1-beta.3-rc2-adapter.1',tgzSha256='854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5',historicalDocumentation=['README.md','ALPHA2-ADAPTATION.json','bundle/README.md'],assemblyTimeOnly='RC2-ADAPTATION.json is the initial transform receipt, not a current platform certification result',currentGuide='../README.md',files=rows),indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(status='copied-exactly',files=len(rows),source=str(target))))

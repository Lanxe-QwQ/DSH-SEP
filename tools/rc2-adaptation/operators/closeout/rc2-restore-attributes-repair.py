from pathlib import Path
import json,hashlib,subprocess,shutil
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');R=S/'source'
v=json.loads((S/'source-checkpoint-final/RESTORE-FAILURE.json').read_bytes())
assert len(v['mismatches'])==5 and all(x['equalAfterCrLfNormalization'] for x in v['mismatches'])
p=R/'.github/workflows/.gitattributes';old=p.read_bytes()
assert old==b'.gitattributes -text !eol\nsep-alpha2-macos.yml -text !eol\n'
p.write_bytes(old+b'sep-rc2-macos.yml -text !eol\n')
files=[x['path'] for x in v['mismatches'] if x['path'].startswith('tools/')]
subprocess.run(['git','add','--renormalize','--',*files],cwd=R,check=True)
d=R/'tools/rc2-adaptation/operators/closeout';o=d/'ORIGIN.json';j=json.loads(o.read_bytes())
for name in ['rc2-local-source-checkpoint-r2.py','rc2-restore-attributes-repair.py']:
 b=Path(name).read_bytes();(d/name).open('xb').write(b)
 j['files'].append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
o.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
note='''
源码检查点首次恢复发现5份文本的LF/CRLF差异（工作流和4份元数据），原记录保留在
source-checkpoint-final/RESTORE-FAILURE.json；当前仅对该工作流固定字节并按既有
局部属性重录元数据，不改程序或安装包字节。新的全量恢复核验在 source-checkpoint-final-r2。
'''
p=R/'tools/rc2-adaptation/RESULTS.md';p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8',newline='\n')
shutil.copyfile(p,S/'ADAPTATION-REPORT-FINAL.md')
print(subprocess.check_output(['git','diff','--cached','--stat'],cwd=R).decode())
print('source restore repair prepared')

from pathlib import Path
import json,hashlib,zipfile,re,shutil
s=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');o=s/'windows-packages-r1';sha=lambda b:hashlib.sha256(b).hexdigest();js=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n'
doc='''# RC.2 全新安装

Full 包包含程序；Only 包需要 --host-root 指向已安装官方 DSH 0.2.1-rc.2 的程序目录。先将包完整解压到独立目录，在 PowerShell 使用包内 Node 执行：

```powershell
& '<解压目录>\\runtime\\node\\node.exe' '<解压目录>\\installer.mjs' --destination 'D:\\Apps\\DSH-SEP-RC2'
# Only：
& '<解压目录>\\runtime\\node\\node.exe' '<解压目录>\\installer.mjs' --destination 'D:\\Apps\\DSH-SEP-RC2' --host-root '<官方DSH程序目录>'
```

目标必须不存在，且父目录是真实目录。安装器在写入前验证全部输入，拒绝覆盖和来源改动；安装会创建空白独立库，不修改官方 DSH。使用安装后 start.vbs 打开；在新实例内配置 API key。关闭窗口保留后台，托盘退出停止实例。此安装器没有 review/install 子命令或 --plan 参数。

默认金额护栏：会话累计 100 元，单轮 5 元，共享预算独立；调整设置不清空消费账本。实际 API 账单以服务商为准。记忆使用 BM25 文本检索与分层治理；图像必须通过受控附件入口。模型 API 标识仍是 deepseek-flash，1017 为界面标签。

本轮为 RC.2 隔离适配候选，尚未发布或切换日常版。物理交互、私人插件逐项运行、真实付费调用与生产自动安装更新不在本轮通过声明内。
'''
for base in [o/'support',o/'bundle-full',o/'bundle-sep']:
 (base/'docs/INSTALLATION.md').write_text(doc,encoding='utf-8');readme=(base/'README.md').read_text(encoding='utf-8')
 if '用本包' in readme:
  start=readme.index('用本包');end=readme.index('\n\n兼容范围',start);readme=readme[:start]+'安装命令与依赖要求见 docs/INSTALLATION.md。Only 只读复用经过精确校验的官方程序文件；所有 SEP 适配文件随包提供。'+readme[end:]
 else:assert '安装命令与依赖要求见 docs/INSTALLATION.md' in readme
 (base/'README.md').write_text(readme,encoding='utf-8')
 for name in ['ONLY-SOURCE.md']:
  (base/'docs'/name).write_text('Only 来源契约：docs/ONLY-REQUIRED.json 列出与官方 npm 精确版本、SHA-512 SRI 及成员 SHA-256 均一致的文件。安装器只读 --host-root；任何不一致均拒绝。修改过的宿主模块属于随包适配 payload；不会从旧宿主覆盖。目标为官方 DSH 0.2.1-rc.2。\n',encoding='utf-8')
archives=[];privacy=[]
for kind in ['full','sep']:
 root=o/('bundle-'+kind);m=json.loads((root/'manifest.json').read_bytes())
 for row in m['support']:
  b=(root/row['path']).read_bytes();row.update(size=len(b),sha256=sha(b))
 (root/'manifest.json').write_text(js(m),encoding='utf-8');matches=[];scanned=0
 for p in root.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(root).as_posix()
  if p.name=='.env' or '.git' in p.relative_to(root).parts or rel.startswith(('home/sessions/','state/','data/')):matches.append({'path':rel,'kind':'private-file-name'})
  if p.suffix.lower() not in ['.js','.mjs','.cjs','.json','.yml','.yaml','.md','.txt','.ps1','.vbs','.html','.css','.xml'] or p.stat().st_size>32*1024*1024:continue
  b=p.read_bytes()
  try:v=b.decode('utf-8')
  except UnicodeDecodeError:continue
  scanned+=1
  for label,pattern in [('user-path',r'(?:C:[\\/]+Users[\\/]+PUBLIC_USER|PUBLIC_ACCOUNT_ID|D:[\\/]AIData[\\/]ProjectWork[\\/]DSH[\\/]rc2-adaptation-20261018-r1)'),('api-key',r'\bsk-[A-Za-z0-9]{25,}\b')]:
   if re.search(pattern,v,re.I):matches.append({'path':rel,'kind':label})
 privacy.append({'kind':kind,'textFilesScanned':scanned,'matches':matches,'scope':'defined text extensions <=32MiB plus private filename exclusions; binary introspection not exhaustive'})
 if matches:continue
 dest=o/('DSH-SEP-'+('Full' if kind=='full' else 'Only')+'-Windows-x64-RC2-preview.zip')
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(root).as_posix())
 h=hashlib.sha256()
 with dest.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 archives.append({'kind':kind,'path':str(dest),'size':dest.stat().st_size,'sha256':h.hexdigest()})
(o/'PRIVACY-SCAN.json').write_text(js({'schema':1,'status':'fail' if any(r['matches'] for r in privacy) else 'pass','results':privacy,'privateInputImported':False,'comprehensiveBinaryAudit':False}),encoding='utf-8');assert len(archives)==2,privacy
(o/'ARCHIVES.json').write_text(js({'schema':1,'status':'pass','archives':archives}),encoding='utf-8')
verification=s/'source/tools/rc2-adaptation/windows-verification';verification.mkdir();orig=[]
for p in sorted((s/'source/tools/alpha2-windows/verification').iterdir()):
 if not p.is_file():continue
 b=p.read_bytes()
 if p.suffix in ['.mjs','.json','.md']:
  v=b.decode('utf-8').replace('alpha2-windows-packages-20261015-r1','rc2-adaptation-20261018-r1\\\\windows-packages-r1').replace('0.2.1-alpha.2','0.2.1-rc.2').replace('0.2.1-beta.3-alpha2-adapter.1','0.2.1-beta.3-rc2-adapter.1').replace('windows-package.2','windows-package.rc2.1');b2=v.encode()
 else:b2=b
 (verification/p.name).write_bytes(b2);orig.append({'path':p.name,'sourceSha256':sha(b),'resultSha256':sha(b2)})
(verification/'ORIGIN.json').write_text(js({'schema':1,'scope':'existing fresh installer/archive/default-desktop operator ported to exact RC.2 stage and versions; original source unchanged','files':orig}),encoding='utf-8')
spec={'schema':1,'expected':{'hostVersion':'0.2.1-rc.2','sepVersion':'0.2.1-beta.3-rc2-adapter.1','revision':'windows-package.rc2.1'},'archives':archives,'outputRoot':str(o/'fresh-install-r1'),'python':r'C:\Users\PUBLIC_USER\AppData\Local\Programs\Python\Python313\python.exe','hostRoot':str(o/'official-donor'),'guardRecords':[]};(o/'INSTALL-SPEC.json').write_text(js(spec),encoding='utf-8');print(js({'status':'pass','archives':archives,'privacy':privacy}))

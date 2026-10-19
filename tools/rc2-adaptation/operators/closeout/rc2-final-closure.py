from pathlib import Path
import json,hashlib,zipfile,tarfile,shutil
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');R=S/'source/tools/rc2-adaptation'
H=lambda b:hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(js(x))
def load(p):return json.loads(p.read_bytes())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
# Fresh native result is required; no conversion of pending to pass.
zpath=S/'evidence/mac-ci-r13/artifact.zip'
verified=load(zpath.with_suffix('.verified.json'));assert verified['status']=='pass'
with zipfile.ZipFile(zpath) as z:
 def read(n):
  b=z.read(n);row=next(x for x in verified['members'] if x['path']==n)
  assert len(b)==row['bytes'] and H(b)==row['sha256'];return json.loads(b)
 mac=read('installer-integration/RESULT.json')
 startup=read('installer-integration/installed-startup/RESULT.json')
 restore=read('installer-restored/RESULT.json')
 integration=read('installer-integration/INTEGRATION.json')
assert mac['status']=='pass' and mac['sourceCommit']=='5104acfb964edb29d1d1f033fb1d0a0e304f14cd'
assert mac['cleanup']==[] and startup['cleanup']==[]
assert mac['fixedDefinitions']=={'tests':6,'pass':6,'fail':0,'cancelled':0,'skipped':0}
assert mac['currentSources']['manifestSha256']=='0d20ff00bf69bf127551d77752d1f97ee1e271845fad8cb5613e052cf9dc9067'
assert mac['original']['status']=='pass' and mac['original']['accountUnchanged'] is True
assert mac['original']['forcedTermination'] is False and mac['original']['normalWaitExit']==dict(code=0,signal=None)
assert mac['integration']['status']=='pass' and mac['integration']['dataRootMatchesApplication'] is True
assert mac['integration']['dataRoot'].endswith('/Library/Application Support/DSH SEP/rc2-mac-finder-preview')
assert mac['integration']['dataRoot']==mac['integration']['nativeSnapshotDataRoot']
assert mac['installedStartup']['status']=='pass' and mac['installedStartup']['cycles']==2
assert startup['status']=='pass' and len(startup['cycles'])==2 and all(x['status']=='pass' for x in startup['cycles'])
assert all(x['exitCode']==0 and x['signal'] is None and not x['timedOut'] for x in mac['commands'])
pin=load(R/'macos/installer-validation/installer-pins.json')
assert restore['source']==pin['installer'] and restore['status']=='pass'
assets=[
 ('Windows Full','windows-packages-r1/DSH-SEP-Full-Windows-x64-RC2-preview-r3.zip',519849282,'8d09dfd24964444dca78ba0852ac4e028bb49ae0d0ef45325e11a3bd7ec058c1'),
 ('Windows Only','windows-packages-r1/DSH-SEP-Only-Windows-x64-RC2-preview-r3.zip',429587818,'8d50e9b8b64b2969bb9f85bcebfdae7b26a260342fd21d20dd777c9a4dac4754'),
 ('Linux','artifacts/DSH-SEP-Linux-x64-RC2-preview-r2.tar.gz',453019592,'e9693f34d1ec23eb1ec5928ce9e476048bda8024467f440074a436fa5ecdaf68'),
 ('macOS','artifacts/macos-r12/DSH-SEP-macOS-RC2-installer-preview.zip',862171913,'1c3a62ae966fe21b58e9ee6a63841cd5e9a30b8415e292b5008dec03b9941a77')]
rows=[]
for name,path,size,sha in assets:
 p=S/path;assert p.stat().st_size==size and digest(p)==sha
 rows.append(dict(platform=name,path=path,bytes=size,sha256=sha))
assert pin['installer']['archiveSha256']==rows[-1]['sha256'] and pin['installer']['archiveBytes']==rows[-1]['bytes']
assert load(S/'windows-packages-r1/fresh-final-r4/RESULT.json')['status']=='pass'
assert load(S/'evidence/LINUX-DELIVERY-r2.json')['status']=='pass'
macproof=dict(schema=1,status='pass',scope='specified native macOS 15.7.9 ARM64/APFS isolated preview; not complete public certification',applicationSourceCommit=pin['payload']['commit'],installerSourceCommit=pin['installer']['commit'],installationSourceCommit=mac['sourceCommit'],runId=39135657506,jobId=117699525433,artifactId=verified['artifactId'],rawArtifactSha256=verified['sha256'],sourceManifestSha256=mac['currentSources']['manifestSha256'],installer=rows[-1],nativeDefinitions=103,postBuildDefinitions=46,namespaceNativeGuards=3,independentIntegrationDefinitions=mac['fixedDefinitions'],installedColdBootCycles=2,currentNamespacePlan=True,cleanup=mac['cleanup'],cleanupInterpretation='no recovery/force/test cleanup needed in this successful run; scoped tracked lifetimes only, not a global process census',originalInstallerExternalButtonInput='not_run',fullPublicCertification='blocked',notVerified=mac['notVerified'],supersededInstaller='bd3316100ac6912728bc5c4fffdb090f125e8e42b7cac684ac3b424a4cb490de')
save(S/'evidence/MAC-CURRENT.json',macproof)
save(R/'macos/FINAL-VERIFICATION.json',macproof)
# Explicit byte reconciliation separate from actual execution receipts.
checks=[]
candidate=load(R/'CANDIDATE-SOURCE.json');assert len(candidate['files'])==445
for x in candidate['files']:
 b=(R/'candidate'/x['path']).read_bytes();assert len(b)==x['bytes'] and H(b)==x['sha256']
checks.append(dict(name='runtime-source',files=445,status='pass'))
overlay=R/'desktop-source-overlay.zip';assert digest(overlay)=='4e18119158c0c42a5595b315225b8d93bf2c7c71ff4f2ccb0cfa6a831a4da070'
with zipfile.ZipFile(overlay) as z:assert len(z.infolist())==359
checks.append(dict(name='desktop-overlay',files=359,status='pass'))
n=0
with tarfile.open(S/'artifacts/linux-runtime-source-r7.tar') as t:
 for m in t.getmembers():
  if not m.isfile():continue
  name=m.name.removeprefix('./');assert not name.startswith('/') and '..' not in name.split('/')
  assert t.extractfile(m).read()==(R/'linux/runtime'/name).read_bytes();n+=1
assert n==282;checks.append(dict(name='linux-source',files=n,status='pass',scope='source bytes; product modes separately manifest-bound'))
# Archive the old drafts with a clear non-current name.
for file in ['README.md','RESULTS.md']:
 shutil.copyfile(R/file,R/(file.removesuffix('.md')+'-PRE-CLOSEOUT.md'))
result=(R/'RESULTS.md').read_text(encoding='utf-8')
result=result[:result.find('\r\n> Mac 当前状态更正')] if '\r\n> Mac 当前状态更正' in result else result
result=result.replace('原生安装器构建及独立新机安装验证仍在进行','修正版独立新机安装验证已通过')
result=result.replace('独立全新机安装链路仍在执行 | artifacts/macos-r9/DSH-SEP-macOS-RC2-installer-preview.zip','修正版原生安装、6项断言及已安装应用两次冷启/正常退出通过 | artifacts/macos-r12/DSH-SEP-macOS-RC2-installer-preview.zip')
start=result.index('Mac 范围是 macOS');end=result.index('\n## 隐私与证据纪律',start)
result=result[:start]+'''Mac 范围是 macOS 15.7.9 ARM64 / APFS。当前安装包 862171913 字节，SHA-256
`1c3a62ae966fe21b58e9ee6a63841cd5e9a30b8415e292b5008dec03b9941a77`。
R9 应用构建源为 `1027e597c53b6d31f734026d97adb1fb4b2426bf`，保持原字节；
修正安装器构建源为 `fecf8489d4bc98e2cac515b2a705b861bda89b9d`；
独立安装验证源为 `5104acfb964edb29d1d1f033fb1d0a0e304f14cd`，
原生 run `39135657506`。原安装器正常打开/关闭；新复制的测试安装器使用真实
NSButton/NSAlert 控件，6项固定断言通过；原生持久计划中的 dataRoot 与实际
RC.2 应用一致；安装后两次冷启/正常退出通过。回执 cleanup 为空：本次成功路径
不依赖强杀、受控恢复或测试补清理；只证明所跟踪生命周期，不是全系统进程普查。

R9 旧安装器仍查 Alpha.2 资料目录，已被取代。R11 的空白安装通过仅证明当时
场景，不能证明现有 RC.2 库保护。修正后另用实际生产 helper 复现旧版漏检，
证明新版识别现存合成 RC.2 目录，并在创建目标/事务前拒绝，3项原生检查通过。
随后围绕固定 R9 应用重建安装器，并对这个精确新 ZIP 完成上述独立安装复验。
原始失败/旧包仍保留，见 `macos/NAMESPACE-REPAIR.md`。

大型工件因工具512MiB限制用分片转回；整包及每片哈希核对，分片未重建/改签。
原应用工件7片，修正安装器4片。应用、安装器、验收源提交分别记录，不混用。
''' + result[end:]
result=result.replace('Mac 原包 52992 个文件、\n2569838745 个解压字节','Mac 修正包 52992 个文件、\n2569838742 个解压字节')
result=result.replace('独立 Mac 安装结果与最终恢复检查点需待收尾回执补入。','独立 Mac 安装结果已绑定；最终源码恢复检查点在外部 CHECKPOINT/RESTORE 记录中绑定最终本地提交。')
if '> Mac 当前状态更正' in result:result=result.split('> Mac 当前状态更正')[0].rstrip()+'\n'
result+='''
## 最终包与复核入口

精确资产及 SHA-256 见 `FINAL-VERIFICATION.json`。Windows 当前结果
`evidence/WINDOWS-CURRENT.json`、Linux `LINUX-DELIVERY-r2.json`、Mac
`MAC-CURRENT.json` 分别保留范围。Mac原始回执 ZIP 在 `evidence/mac-ci-r13`。
这些路径相对于上述 D 盘证据根，不表示它们已上传到公共仓库。

`macos/installer-validation/README.md` 和该目录 `INPUTS.json` 保留5104提交执行前
固定输入，pending描述该代准备时状态；当前结果以 `macos/FINAL-VERIFICATION.json`
为准。既有平台说明中的其他未认证项继续有效，本轮没有逐项重跑所有历史场景。
'''
(R/'RESULTS.md').write_text(result,encoding='utf-8',newline='\n')
readme=(R/'README.md').read_text(encoding='utf-8')
readme=readme.replace('## 当前进度（收尾中）','## 当前结果（限定环境隔离预览）')
readme=readme.replace('原生安装器构建及独立新机安装验证仍在进行。','修正版原生安装器、独立全新安装、6项断言及已安装应用两轮冷启/正常退出通过。')
readme=readme.replace('R9 安装器仍检查 Alpha.2 数据目录，已确认与 R9 应用的 rc.2 目录不一致，现已被修正版流程取代。R11 空白安装正例仅作历史证据；','R9 安装器被修正版 R12 取代，修正版已完成独立原生安装与重启验证。R11 空白安装正例仅作历史证据；')
readme+='\n[当前验证记录](RESULTS.md) · [输入与复验导航](REPRODUCTION.md) · [精确资产绑定](FINAL-VERIFICATION.json)\n'
readme+='\nMac `installer-validation/README.md` 与 `INPUTS.json` 保留5104执行前固定输入，pending仅指当时；当前结果见 `macos/FINAL-VERIFICATION.json`。既有平台未认证项继续有效。\n'
(R/'README.md').write_text(readme,encoding='utf-8',newline='\n')
ns=R/'macos/NAMESPACE-REPAIR.md';old=ns.read_bytes();shutil.copyfile(ns,R/'macos/NAMESPACE-REPAIR-PRE-CLOSEOUT.md')
ns.write_text('''> 最终状态：修正版精确ZIP的独立原生安装验证已通过，源5104acfb、run39135657506。
> 真实持久计划绑定RC.2目录、6项固定断言和安装后两轮冷启/正常退出通过。
> 成功路径cleanup为空，不依赖强杀或后续测试清理。以下保留准备阶段的历史说明，
> 其中pending仅描述当时状态；现行结果见FINAL-VERIFICATION.json。

'''+old.decode('utf-8'),encoding='utf-8',newline='\n')
proof=dict(schema=1,status='pass',scope='isolated RC.2 adaptation closeout in the individually stated environments; not complete cross-platform certification',officialTag='dsh-v0.2.1-rc.2',officialCommit='687f282e8625c6b8d11ff58211a90524be2e4317',sepInternalVersion='0.2.1-beta.3-rc2-adapter.1',assets=rows,sourceReconciliation=checks,common=dict(tests=49,passCount=49,logSha256=digest(S/'evidence/core-regression-r3.tap'),replaySha256=digest(S/'evidence/REPLAY-COMPARISON.json')),windows=dict(record='evidence/WINDOWS-CURRENT.json',sha256=digest(S/'evidence/WINDOWS-CURRENT.json'),desktopOverall='blocked',desktopCore='pass',dailyEntrySnapshot='not_run'),linux=dict(record='evidence/LINUX-DELIVERY-r2.json',sha256=digest(S/'evidence/LINUX-DELIVERY-r2.json'),nativeDefinitions=66,waylandRounds=2,stepsPerRound=10),mac=dict(record='evidence/MAC-CURRENT.json',sha256=digest(S/'evidence/MAC-CURRENT.json'),nativeDefinitions=103,postBuildDefinitions=46,namespaceGuards=3,freshIntegrationDefinitions=6,coldBootCycles=2),notVerified=['Complete cross-platform public certification','Current private library continuation in this adaptation','Paid online providers','Physical Windows/Mac input and tray interactions','Windows unsigned start.ps1 under current execution policy','Mac Developer ID/notarization','Broader Linux/macOS hardware and desktop environments','Production public auto-install positive path'],dailySwitched=False,mainChanged=False,releasePublished=False,authorizedMacTestBranch='codex/sep-rc2-macos-20261018')
save(S/'evidence/FINAL-VERIFICATION.json',proof);save(R/'FINAL-VERIFICATION.json',proof)
# Current byte indices are intentionally not execution evidence.
for folder in ['tests','runtime','build','windows-verification','linux','macos']:
 d=R/folder;rows=[]
 for p in sorted(d.rglob('*')):
  if p.is_file() and p.name!='CURRENT-INPUTS.json' and 'node_modules' not in p.parts:
   rows.append(dict(path=p.relative_to(d).as_posix(),bytes=p.stat().st_size,sha256=digest(p)))
 (d/'CURRENT-INPUTS.json').write_text(js(dict(schema=2,scope='current source bytes only; not an execution receipt',isExecutionEvidence=False,files=rows)),encoding='utf-8',newline='\n')
save(S/'evidence/SOURCE-PREFLIGHT-r2.json',dict(schema=2,status='pass',scope='source-byte reconciliation; actual native execution receipts remain separate',checks=checks,macInstallationCommit=mac['sourceCommit']))
shutil.copyfile(R/'RESULTS.md',S/'ADAPTATION-REPORT-FINAL.md')
print(js(dict(status='closed-in-scope',assets=len(assets),macRun=39135657506,dailySwitched=False,releasePublished=False)))

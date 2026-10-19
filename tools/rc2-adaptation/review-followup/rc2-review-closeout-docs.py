from pathlib import Path
import json,hashlib,re,shutil,subprocess
S=Path(r'D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1');R=S/'source';T=Path(r'D:\AIData\ProjectWork\DSH\rc2-review-followup-20261019-r1');O=R/'tools/rc2-adaptation/review-followup'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
green=(T/'GREEN-r2.log').read_bytes();assert re.search(rb'Ran 12 tests',green) and b'FAILED' not in green and re.search(rb'\bOK\s*$',green)
rows=[]
for name in ['RED.log','GREEN.log','GREEN-r2.log','TEST-INPUT-r1.py']:
 p=T/name;rows.append(dict(path=name,bytes=p.stat().st_size,sha256=H(p.read_bytes())))
record=dict(schema=1,status='pass',scope='local offline metadata/guard/source-derivation and immutable-input verification; not a remote publication or native product rerun',reviewedCommit='2201098a3359bde5c0d8a0594d1d9b56b5b17457',fixedDefinitions=12,passCount=12,failCount=0,errors=0,testInput=dict(path='review_regressions.py',sha256=H((O/'review_regressions.py').read_bytes())),logs=rows,attempts=[dict(log='RED.log',status='fail',scope='before repairs, includes missing governance and owner mapping'),dict(log='GREEN.log',status='fail',scope='11 definitions pass, one test incorrectly used r instead of existing row; no production change was made to satisfy it'),dict(log='GREEN-r2.log',status='pass',tests=12)],reviewDispositions={'1':'fixed: old byte-identical copy preserved in history/pre-r4; verified current r4 pointer','2':'fixed locally: current owner/main-only guards and canonical links; explicit single hash-bound Beta2 derivative','3':'accepted hygiene: frozen generated helper unchanged; comment and module labels recorded; future rebuild required for cleanup','4':'accepted documented one-shot tooling scope'},testedArchivesUnchanged=4,candidateFilesUnchanged=445,remoteWorkflowExecution='not_run',nativeRevalidation='not_run; no delivered program byte changed',dailySwitched=False,releasePublished=False,mainChanged=False)
save(O/'RESULT.json',record);save(T/'RESULT.json',record)
text='''# KIMICODE RC.2 审查响应（本地流程修订）

审查基线 `2201098a3359bde5c0d8a0594d1d9b56b5b17457`。本轮修订属于后续本地
源码提交，不改此前四份安装包、445文件候选、固定Mac helper或历史发布输入。
没有切换日常版，没有推送GitHub，也没有触发发布工作流或创建Release。

## 逐项处置

1. **旧代次tgz误取：已修正。** 顶层旧包SHA-256为
   `f80533561f1c91beab7656f014fa56e05936489a94224cd1f9913766416c8ca8`；
   当前r4包为 `854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5`。
   检查现行构建、Mac钉扎、Linux输入与CONTINUATION均选r4/嵌入副本后，先复制
   旧字节并核对摘要，再撤去顶层同名文件。原始字节现存于
   `artifacts/history/pre-r4/`，带SUPERSEDED.json与禁止安装标识；旧日志原样保留，
   通过原路径/新路径/摘要对账。当前入口为artifacts/CURRENT-CANDIDATE.json。
   该入口仅标明正确构建输入，不代表批准日常部署或公开发布。
   我独立遍历唯一tar正文成员，实际为**4个**差异，而非报告所写5个：
   RC2-ADAPTATION.json、alpha2-subagent.js、project-binding.js、session-parent-proof.js。

2. **仓库更名：本地已修正。** GitHub只读核验现名为Lanxe-QwQ/DSH-SEP。
   两个relay的仓库守卫、实际API目标、根package仓库URL与README下载链接同步。
   手动触发、仅main、草稿/预发布、固定版本/计划/摘要等限制保留。
   Beta.2还会取得哈希固定的旧relay.py，其内部仍写Lance，不能只改外层URL。
   本轮保留历史release文件不变：先校验源摘要66440f56…，精确单处替换归属名，
   再校验派生摘要d5f7715f…。篡改源、缺失锚点和重复应用均拒绝。
   旧计划内公开GitHub基础下载地址保持原字节，其无凭据重定向机制不变。
   两个relay仍是Beta.1/Beta.2专用，不因此成为RC.2的通用发布器。
   本轮只做离线门禁、派生与语法验证，实际远端工作流执行为not_run。

3. **生成helper路径：接受为卫生项，保留固定字节。** SHA-256仍为261a3377…。
   53处路径注释之外，还存在46处esbuild模块工厂标识，不能只去注释就声称已脱敏。
   路径指向D盘实验构建布局，未据此认定泄漏凭据；也不宣称穷尽隐私审计。
   当前产物已被构建/来源/原生回执绑定，未静默重写。下次重建采用受控相对源根，
   产生新指纹并完成原生复验后再替换；本轮不宣称此项已清理。

4. **一次性operators：保留现有已声明边界。** 它们是有固定阶段路径且常排他创建
   输出的实验工具，不是通用安装入口，不宜直接重复执行。没有为消除文字命中
   而批量改写历史脚本和证据。

## 验证与证据范围

离线回归12/12通过，含新仓库main正例、旧仓库/分叉/其他分支及标签负例、
派生篡改/重复应用拒绝、历史发布输入不变、候选445文件与四份安装包摘要不变。
测试没有安装程序、调用模型、上传或修改远端Release。固定Mac helper未重建，
没有把已有原生通过记录伪称为本次新代码执行记录。

RED、一次中间失败与最终GREEN均保留。中间失败是测试把现有变量row误写为r；
更正断言后通过，没有改生产逻辑迎合测试。日志与两代测试输入由RESULT.json绑定。
外部证据根为 `D:\\AIData\\ProjectWork\\DSH\\rc2-review-followup-20261019-r1`。

补充范围说明：仓内PUBLIC-SOURCE-SCAN.json绑定的是ac69bda3…、19498项历史
公开源码基线，**不覆盖后来的RC.2增量或本轮修订**。根README也保留“本地实验脚本
含本机路径、当前分支尚未作为公开源码分发”的提示。不能用旧扫描替代新发布前扫描。
完整跨平台认证、付费模型、物理输入、公证、PS1机器策略等原有未认证项不变。
'''
with (O/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
for filename in ['rc2-review-inspect.py','rc2-review-quarantine.py','rc2-review-repository-repair.py','rc2-review-closeout-docs.py']:
 b=Path(filename).read_bytes();(O/filename).open('xb').write(b)
files=[]
for p in sorted(O.iterdir()):
 if p.is_file():files.append(dict(path=p.name,bytes=p.stat().st_size,sha256=H(p.read_bytes())))
save(O/'INPUTS.json',dict(schema=1,scope='current review follow-up source and evidence byte index; logs are separate execution evidence',files=files))
shutil.copyfile(O/'README.md',T/'REVIEW-RESPONSE.md')
p=R/'tools/rc2-adaptation/README.md'
with p.open('ab') as f:f.write('\n2026-10-19流程审查响应见 [review-followup/README.md](review-followup/README.md)；原安装包与运行时指纹保持不变。\n'.encode('utf-8'))
print(json.dumps(dict(status='documented',tests=12,archivesUnchanged=4,helperUnchanged=True,publicWorkflow='not_run')))

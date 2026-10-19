# DSH 0.2.1-rc.2 隔离适配记录

本记录针对官方 tag `dsh-v0.2.1-rc.2` / 提交
`687f282e8625c6b8d11ff58211a90524be2e4317`。SEP 是内部 Beta 派生候选
`0.2.1-beta.3-rc2-adapter.1`；宿主 rc.2 不代表 SEP 进入 RC。
本轮未切换日常版、未修改 GitHub main、未发布 Release。Mac 原生执行只使用
已授权的专用测试分支。以下数字均按各自输入与场景记录，不相加宣称全面认证。

## 接口适配

1. 精确固定 RC.2 主包、依赖与 peer；稳定 invariants 叶子版本保持受控例外，
   不把“同版本号”当作所有组件都需重命名。
2. 对新 JSONL 资源插件保留官方 apply/lifetime，注入 SEP 存储后端，保持
   消费者与存储的真实关闭顺序。
3. 适配官方移除的旧 toolFilter：在 suite_delegate 创建的子任务派发前验证
   精确身份，再由真实 agent/created 钩子限制工具。并发/统一取消等承诺只覆盖
   suite_delegate 创建的任务；Profile 模型与预算拦截单独生效。
4. 四个预设（含 Minimal）的原生压缩引擎由 SEP 受控引擎接续，保留原生命令与
   pruner，不重复运行两个压缩引擎。
5. 1017 是模型显示名称更新，API 仍使用 deepseek-flash。新增原生 Search/Fetch
   保留官方默认选择，已做真实 SDK + loopback 合成正负例；未调用付费在线提供方。
   它们不产生辅助模型账目，不能据此断言独立服务免费或其费用已被模型账本覆盖。
6. 重编译桌面与五个前端组件，移植受控启动、当前项目 fd4、品牌、预算/记忆设置
   和更新等既有接口；新增 RC.2 版本门禁，不放行未知未来版本。

## 平台结果与精确包

| 平台 | 当前结果 | 包 |
| --- | --- | --- |
| Windows x64 Full/Only | 最终 ZIP 全新安装、拒绝覆盖/篡改、原宿主 donor 不变、运行时冒烟通过；另有并行宿主和每种包两轮桌面核心记录 | windows-packages-r1 下 Full/Only RC2-preview-r3.zip |
| Linux x64 | 66 原生定义、两轮私有原生 Wayland 各10步、最终 tar 还原安装及两次 headless 冷启通过 | artifacts/DSH-SEP-Linux-x64-RC2-preview-r2.tar.gz |
| macOS ARM64 | 103 原生、46 文档/附件/上下文、原应用两轮 LaunchServices 冷启/正常退出、安装器构建/签名/恢复通过；独立全新机安装链路仍在执行 | artifacts/macos-r9/DSH-SEP-macOS-RC2-installer-preview.zip |

Windows 最终原包安装回执为 `windows-packages-r1/fresh-final-r4/RESULT.json`。
宿主/桌面功能记录来自执行图一致的受测安装；最终包文档变更另有逐成员差异证明。
当前机器直接执行未签名 start.ps1 被执行策略拒绝，原始桌面总回执保持 blocked，
桌面核心结果另列 pass；未修改系统执行策略。无 observer 的首次启动、物理托盘
操作等仍列未验证，不据此声称整个 Windows 环境全面认证。
最终安装测试可选日常入口指纹列表为空，其命名循环检查不能证明日常入口哈希
前后一致；本轮安装目标均被限制到新建 D 盘隔离目录，未执行日常切换。

Linux 范围是 WSL2 Ubuntu 24.04 x64/ext4/私有 Sway 原生 Wayland，不代表所有
GNOME/KDE/物理硬件。Wayland 用 installed-r7，最终 r8 只变 README 内容/权限并
加来源记录；完整条目（含模式与链接）对账确认运行代码相同，最终 tar 实装为 r9。

Mac 范围是 macOS 15.7.9 ARM64 / APFS。安装包 862171912 字节，SHA-256
`bd3316100ac6912728bc5c4fffdb090f125e8e42b7cac684ac3b424a4cb490de`。
R9 构建源为 `1027e597c53b6d31f734026d97adb1fb4b2426bf`；独立安装验证源为
`61742ad8a37e7f3923a212dca602f01ea51d77b6`。后者必须先校验固定前次原工件的
元数据、整包哈希、全部成员、签名与清单，再执行原生交互。1.71GB 工件因工具
512MiB 限制通过七片转回，重组哈希与原对象一致；分片未重建或改签程序。

## 隐私与证据纪律

Windows 定义的文本/文件名扫描通过，二进制审计不穷尽。Mac 原包 52992 个文件、
2569838745 个解压字节的定义签名扫描出现6个命中，原始扫描保留 blocked。
逐项复核为引号/NUL 终止的 PEM 格式标记、公开 Shiki Emacs Lisp 语法标识符，
外部文件与锁定官方依赖哈希一致，ASAR 内上下文一致；复核 pass，0项未解释。
没有发现本次定义的个人路径、GitHub 令牌或私有状态文件名命中。
这不是穷尽性语义/二进制隐私认证，comprehensivePrivacyAudit 保持 false。

保留各代失败：Zod/peer 定位、Electron original-fs 识别、ASAR unpacked 代次替换、
当前项目 owner/fd4 组合、已转换 context 再套旧源钉扎等。首次失败不被后续通过
改写；context 导入失败导致的服务缺失按同一根因的后果记录。一次下载 TLS
握手中断在建文件前重试，只是只读传输问题。29.7分钟安装器构建耗时不是运行时
性能对照，不据此计算软件开销。

完整跨平台公开认证仍 blocked。物理输入、现有私人库本轮接续、付费在线模型、
Mac Developer ID/公证、更多 Linux/Mac 环境、生产自动安装更新正例等未认证项
继续保留；本轮没有扩大固定标准。公网自动安装正例仍沿用此前搁置状态。

当前源码在 `candidate/`（445文件）、`build/`、`windows-verification/`、
`linux/runtime/` 与 `macos/`；根 package 保留历史，不用它生成当前 RC.2 候选。
桌面完整修改源码另由359文件覆盖包绑定。CURRENT-INPUTS 是当前源码字节索引，
不是执行回执。所有外部原包、原始日志与最终源恢复检查点分别绑定；本记录的
独立 Mac 安装结果与最终恢复检查点需待收尾回执补入。

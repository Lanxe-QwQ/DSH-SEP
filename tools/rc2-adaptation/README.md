> 记忆修复候选 memory-repair.1：三项缺陷的当前实现与证据见 [修复入口](../memory-repair/README.md)。这是隔离候选；公开下载和日常版仍为原 Beta.4。下文原适配/发布记录保留历史语义。

> Mac 当前状态更正：R9 安装器被修正版 R12 取代，修正版已完成独立原生安装与重启验证。R11 空白安装正例仅作历史证据；见 [目录保护修正](macos/NAMESPACE-REPAIR.md)。R9 应用原包保持不变。

# DSH 0.2.1-rc.2 隔离适配与源码导航

固定官方提交 `687f282e8625c6b8d11ff58211a90524be2e4317`，tag
`dsh-v0.2.1-rc.2`。SEP 内部候选 `0.2.1-beta.3-rc2-adapter.1`，其
Beta 成熟度不会因宿主的 rc.2 标识而改变。本轮不切换日常版、不改 main、
不发布 Release；仅授权的 Mac 专用测试分支与原生 CI 用于复验。

## 当前受测源码

- `candidate/`：445 个文件的实际套件输入，逐字节绑定
  `CANDIDATE-SOURCE.json` 和 tgz SHA-256
  `854b8dd3c82c7a2d7b26b6a5a14ba3488b293b39b922cd4f5e35347f0ecf40a5`。
- `runtime/` 与 `derive-runtime.mjs`：rc.2 子代理与会话插件生命周期适配。
- `build/`、`windows-verification/`：Windows 宿主、客户端、桌面、Full/Only
  装配和真实隔离安装核验。完整变更源码另有 359 文件的
  `desktop-source-overlay.zip`，必须覆盖到上述固定官方源码，而非任意版本。
- `linux/runtime/`：原生 Linux 实际运行入口、受控副本、事务、监督、附件与
  Wayland 载具；WSL2 Ubuntu 24.04 x64/ext4/私有 Sway 范围。
- `macos/`：当前 Mac 原生装配、精确 capture、103 项基础原生、46 项
  文档/上下文/附件、真实应用两次启动及安装器验证入口。
- `operators/`：已用过的一次性 D 盘装配/对账脚本，不是产品安装入口。

根 package.json 及原始 `bundle/` 保留为历史基线。当前套件源要审查
`candidate/`；不要用根目录的旧入口生成 rc.2 包。`candidate/README.md`、
`candidate/ALPHA2-ADAPTATION.json`、`candidate/bundle/README.md` 是保留原字节的
历史捕获输入；`candidate/RC2-ADAPTATION.json` 是装配前的转换记录，里面的
not_run 不能代表后续平台复验状态。当前状态以本说明与本轮最终证据索引为准。
这些历史文件不被暗改为“已通过”。

## 当前结果（限定环境隔离预览）

共同核心 49 项、445 文件转换重放一致；Linux 66 项原生和两轮 Wayland
交互通过。Mac 103 项原生、46 项后构建、真实应用两次冷启动/正常退出通过，
修正版原生安装器、独立全新安装、6项断言及已安装应用两轮冷启/正常退出通过。Windows Full/Only 最终 ZIP 的全新安装、完整性、拒绝覆盖和运行时冒烟已通过
（fresh-final-r4）；并行宿主和桌面核心另有通过记录。

以上是各自输入范围的结果，不能相加后声称所有功能或私人插件全部认证。
Windows 直接运行未签名 start.ps1 在当前机器执行策略下仍 blocked；标准
VBS/桌面核心记录另列。物理输入、现有私人库在本轮接续、付费提供方、Mac
Developer ID/公证及更广泛 Linux/Mac 环境仍未认证。

原生 Search/Fetch 保持官方默认选择；启用它们不会产生辅助模型账目，不能
据此认定独立服务免费或已计入模型账本。合成测试未调用付费在线提供方。

隔离输出与证据根：`D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1`。
`CURRENT-INPUTS.json` 是当前源码字节索引，不是执行证据；每代日志、失败样本、
实际候选包及其哈希分别保留。

[当前验证记录](RESULTS.md) · [输入与复验导航](REPRODUCTION.md) · [精确资产绑定](FINAL-VERIFICATION.json)

Mac `installer-validation/README.md` 与 `INPUTS.json` 保留5104执行前固定输入，pending仅指当时；当前结果见 `macos/FINAL-VERIFICATION.json`。既有平台未认证项继续有效。

2026-10-19流程审查响应见 [review-followup/README.md](review-followup/README.md)；原安装包与运行时指纹保持不变。

# DSH SEP · Windows / Linux / macOS Beta

**DEEPSEEK HARNESS SYSTEM ENHANCEMENT PACKAGE（DSH 系统增强套件）**：为 DeepSeek Harness 提供分层记忆、本地 RAG、预算护栏、受管委派、受控文件修改与恢复。

**当前分发版：0.2.1-beta.4 · 宿主 DSH 0.2.1-rc.2 · SEP 为 Beta。** [下载 Beta.4](https://github.com/Lanxe-QwQ/DSH-SEP/releases/tag/v0.2.1-beta.4)。宿主 RC 不代表 SEP 已达 RC；Linux/macOS 按限定环境预览分发。

| 平台 | 下载 |
| --- | --- |
| Windows x64 Full | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-Full-0.2.1-beta.4-Windows-x64.zip) |
| Windows x64 Only | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-Only-0.2.1-beta.4-Windows-x64.zip) |
| Linux x64 预览 | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-0.2.1-beta.4-Linux-x64.tar.gz) |
| macOS ARM64 预览 | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-0.2.1-beta.4-macOS-arm64.zip) |

[Windows说明](release/v0.2.1-beta.4/Windows.md) · [Linux说明](release/v0.2.1-beta.4/Linux.md) · [macOS说明](release/v0.2.1-beta.4/macOS.md) · [完整发布说明](release/v0.2.1-beta.4/RELEASE-NOTES.md)

四份包用于**全新独立安装**，保留已验构建原字节。Only需精确官方RC.2 npm来源，不是向任意桌面目录加插件；根仓库组合入口的历史准入不等于任意宿主全能力认证。[版本/哈希绑定](release/v0.2.1-beta.4/ASSET-BINDINGS.json) · [旧用户与更新限制](release/v0.2.1-beta.4/UPGRADING.md)。本轮不切换维护者日常版，不发布通用原位更新候选。

## 核心能力

- L1上下文、L2项目/临时事项、L3习惯/重要事实/项目目标、L4按需归档；作用域、保留期和删除依据分别治理。
- 本地RAG采用 **BM25** 词项排序，不依赖外置向量数据库；Mem0消息来源限同项目，提炼捕获默认关闭，启用可能增加token。
- 共享、单会话和单轮预算分别拦截；默认会话100元、单轮5元为估算护栏，改设置不清零账本，不代表服务商实际余额。
- 受管委派、观察后修改、工作副本与恢复。并发/超时/取消/记录承诺只限 suite_delegate 创建的任务；Profile模型/预算拦截单列。Shell与插件保护范围按平台说明。

## 验证与限制

Windows最终ZIP新装/拒绝/冒烟与桌面核心通过，但直接start.ps1受执行策略阻止，整体桌面blocked；Linux限定WSL2 Ubuntu24.04/ext4/私有Sway，历史AT-SPI失败保留；macOS限定15.7.9 ARM64/APFS，ad-hoc签名未公证。Linux/macOS完整公开认证仍blocked。物理输入、广泛硬件/系统环境、全部私人插件、当前私人库接续、付费模型及公网自动安装同次正例尚未全面认证。

[技术细节/BM25](release/v0.2.1-beta.4/TECHNICAL-NOTES.md) · [文档导航](docs/DOCS_INDEX.md) · [当前源码导航](release/v0.2.1-beta.4/SOURCE-GUIDE.md) · [许可与对应源码](release/v0.2.1-beta.4/THIRD-PARTY.md)

当前RC.2源码在 tools/rc2-adaptation/candidate/、平台适配目录及 upstream/官方源归档+桌面overlay；根source/、bundle/和package.json保留历史基线，不能代替当前候选。公开快照不含私人Git历史、未跟踪文件、用户会话/账本/凭据；维护模板的脱敏派生另记，不冒充历史执行字节。

本轮更新了RC.2会话/子代理桥、上下文压缩适配和三平台安装交付；各组证据可能重叠，不合并为完整认证。固定验收标准与历史失败记录保持。

自有代码 [MIT](LICENSE)，第三方保留各自许可。反馈请通过 Issues，勿附API Key、私人正文或完整账本。历史说明见 [上版总览](docs/PRE-BETA4-README.md)；其中时点词不替代当前范围。

历史公开发行：[Beta.3](https://github.com/Lanxe-QwQ/DSH-SEP/releases/tag/v0.2.1-beta.3)；它仍对应 Alpha.2 资产，不是当前 RC.2 下载。

[本次公开发布核验回执](release/v0.2.1-beta.4/PUBLICATION.json)：9份附件的服务器摘要与匿名下载HEAD已核对；源码脱敏清单绑定固定发行标签，main上的后续发布状态变更见 POST-PUBLICATION-OVERLAY.json。

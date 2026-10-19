# DSH SEP 0.2.1-beta.4 · Windows / Linux / macOS Beta

2026-10-19。适配官方 **DSH 0.2.1-rc.2**（固定提交 687f282e），SEP 发布级别仍为 **Beta / prerelease**。

| 选择 | 安装包 |
| --- | --- |
| Windows x64 Full | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-Full-0.2.1-beta.4-Windows-x64.zip) |
| Windows x64 Only | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-Only-0.2.1-beta.4-Windows-x64.zip) |
| Linux x64 预览 | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-0.2.1-beta.4-Linux-x64.tar.gz) |
| macOS ARM64 预览 | [下载](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.4/DSH-SEP-0.2.1-beta.4-macOS-arm64.zip) |

四包按原字节发布，内部构建号不变；详见 ASSET-BINDINGS.json 和 SHA256SUMS.txt。请先阅读 [Windows](Windows.md)、[Linux](Linux.md)、[macOS](macOS.md) 与 [升级边界](UPGRADING.md)。均用于新独立安装，不覆盖官方 DSH、旧 SEP、用户插件和私人数据；本次不切换日常版，也不提供通用原位自动更新候选。

## 变化

移植 RC.2 会话提供方、上下文投影、原生四预设压缩流程并收紧真实子代理作用域工具限制。Windows 使用修复后的 Full/Only r3；Linux r2 完成最终 tar 安装/冷启动与限定 Wayland 补验；Mac R12 修正既有 RC.2 数据命名空间检查，并完成原生精确包全新安装与两次冷启动。

共同核心49项、445文件转换重放、Linux66项及两轮Wayland、Mac103+46项与R13原生安装、Windows最终ZIP安装/拒绝/运行支持与桌面核心均有范围绑定证据，不累加为全部功能认证。Windows直接start.ps1受执行策略阻止，桌面整体blocked而核心pass；Linux的AT-SPI历史失败仍保留；Mac仅ad-hoc签名、未公证。

Linux/macOS完整公开认证仍blocked。物理输入、其他系统环境、全部私人插件、当前私人库接续及真实付费模型未在本轮全面认证。原生Search/Fetch的独立服务账单不由“无辅助模型调用”推定免费。详见 [技术摘要/BM25](TECHNICAL-NOTES.md)、[源码导航](SOURCE-GUIDE.md) 与 [第三方许可](THIRD-PARTY.md)。

源代码、文档、第三方对应源码、分发清单及SHA-256同次提供。源码已作限定脱敏检查，扫描不代表全面隐私认证。SEP自有代码MIT，第三方继续各自许可。

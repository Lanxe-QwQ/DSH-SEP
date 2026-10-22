# macOS ARM64 · DSH SEP 0.2.1-beta.5 隔离预览

固定 DSH `0.2.1-rc.2`；支持已验证的 **macOS 15.7.9 ARM64 / APFS** 环境。完整公开认证仍 **blocked**。应用与安装器重新构建，保留R12已审的命名空间修正。

下载并核对 SHA-256，完整解压，阅读安装器包内说明后打开 `DSH SEP Installer.app`。只接受新独立目标和规定的空白受控数据条件；发现已有 RC.2 数据、未知事务或不满足目录安全条件时会拒绝，不删数据/事务绕过门禁。

仅使用 ad-hoc 签名，没有 Apple Developer ID 或公证，不提供关闭 Gatekeeper/系统安全机制的指引。系统拒绝启动时，本预览不宣称具备正式签名分发体验。

Beta.4历史证据包括103项基础原生与46项后构建检查、R9应用两次LaunchServices冷启，以及R12安装器/R13真实安装与安装后两轮启动。本轮从已审修复候选重新构建app和安装器；保留R12的RC.2命名空间保护，不再使用R9旧app字节。

本轮Mac CI run 39706727364，源码850f71076fdadef74cf78ec98e745e79f0fa5dca。验证包含原生APFS/业务/媒体、65项核心+3轮持久化记忆回归、46项实际app后构建检查、两次LaunchServices正常启动/退出、安装器构建/签名/精确归档恢复。**本轮没有重复原生安装器按钮安装流程**，不把Beta.4的R13原样视为新ZIP安装正例。结果与资产绑定见VERIFICATION.json / ASSET-BINDINGS.json。

这是作用域内资源生命周期证据，不是全系统进程普查。物理鼠标输入、当前私人库接续、付费模型、Intel Mac、其他 macOS 版本、Developer ID/公证仍未认证。原生任意 Shell/MCP 使用已弃用 `sandbox-exec` 的限定兼容层，异常收尾不明时保留隔离与阻断；不承诺未来 macOS 兼容。

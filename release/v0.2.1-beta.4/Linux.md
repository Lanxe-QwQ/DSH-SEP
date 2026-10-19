# Linux x64 · DSH SEP 0.2.1-beta.4 隔离预览

固定 DSH `0.2.1-rc.2`，原构建 `RC2-preview-r2`。仅在 **WSL2 Ubuntu 24.04 x64 / ext4 / 私有 Sway Wayland（无 XWayland）** 范围完成本轮验证。完整公开认证仍 **blocked**。

核对 SHA-256 后使用保留可执行权限/链接的 tar 解包，按包内 README 安装到新目录；使用包内安装入口与 `start.sh`，不要将历史 `operators` 构建脚本当作安装器。需满足包内列明的 Node/用户命名空间、bwrap 与图形会话条件；任何准入失败须保留诊断，不删租约文件强行解锁。新实例不迁移私人库，不覆盖另一个官方 DSH。

本轮 66 项原生测试、两轮每轮 10 步真实私有 Sway/Wayland 交互、最终 tar 实际安装及两次 headless 冷启动通过。测试组可能重叠，不合并成全部独立功能数。已验证受控工作副本/提交/恢复、进程监督租约、会话附件与限定可访问性适配；Shell/MCP 必须经过限定入口，不能据此担保同用户主机任意代码。

历史 AT-SPI 退出点击失败保留；键盘/指针正例不能替代该失败。物理桌面、任意 Wayland 合成器、GNOME/KDE、其他发行版/硬件、付费模型与本轮私人旧库接续尚未认证。POSIX 自动安装仍拒绝 `SEP_POSIX_UPDATE_INSTALL_NOT_INTEGRATED`；本 Release 提供手动新安装包。

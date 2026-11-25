# DSH SEP 0.2.2-beta.1 · Windows x64

面向 Windows x64 的独立安装 Beta，基于 DeepSeek Harness 0.2.3-alpha.2。DSH SEP 为 Harness 增加项目记忆与检索、预算管理、受管文件变更和恢复。

- 恢复左上角独立的 SEP 标识。
- 修复可选 4LM 召回在 Alpha.2 会话写入时触发的 `SEP_SESSION_APPEND_INVALID`。新安装默认关闭 4LM，用户可连接已有 4LM 实例。
- Full 带 DSH 本体与 SEP。Only 带 SEP 和必要适配，从固定版本的官方 Windows 安装包读取所需文件，生成独立实例。两种包的操作说明都在包内 README。 [官方 DSH 供体](https://download.deepseek.com/dsh-desk/bin/win-x64/deepseek-harness-0.2.3-alpha.2-win-x64.exe)

本轮从两份最终 ZIP 分别完成空白安装。Full 验证了未配置 4LM 时的首轮会话。Only 验证了合成 4LM 在第一轮就注入召回、会话落盘，以及未改动的官方 Alpha.2 Web 宿主在 SEP 启动、运行和关闭期间保持可用。两种包均通过桌面启动、会话重读、正常退出及限定范围的隐私扫描。验证使用离线模型。

发行范围为 Windows x64 独立新装。Linux、macOS 和原位更新沿用其各自的已发布范围。SEP 自有部分按 MIT 许可发布，第三方组件继续适用各自的许可。FFmpeg 对应源码、Windows 适配源码与来源说明随本版提供。 [既有 sharp/libvips 对应源码](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.5/THIRD-PARTY-SOURCES.zip)

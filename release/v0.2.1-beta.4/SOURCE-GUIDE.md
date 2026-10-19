# 当前源码与历史基线

本版公开源码是只导出已跟踪 Git blob 的快照；不导入私人 Git 历史、未跟踪文件、运行会话、账本或凭据。

- 官方 DSH 0.2.1-rc.2：upstream/DeepSeek-Harness-0.2.1-rc.2-source.zip（官方 commit 687f282e8625c6b8d11ff58211a90524be2e4317，SHA-256 828bbbebaf507d2b1fc335a608e1c8174e2dd5c5c80ebb64d5146ddc5ecb511f）；来源见 upstream/RC2-SOURCE-ORIGIN.json。
- 当前宿主修改：tools/rc2-adaptation/desktop-source-overlay.zip，359 文件，覆盖上述精确官方源码。相关构建及源依赖按 REPRODUCTION.md。
- 当前 SEP 输入：tools/rc2-adaptation/candidate/，445 文件；CANDIDATE-SOURCE.json 与 RC2-ADAPTATION.json 绑定派生链。根 package.json、bundle/、source/ 是保留的历史基线，不能用根打包命令替代当前候选。
- Windows：tools/rc2-adaptation/build/ 与 windows-verification/；Linux：tools/rc2-adaptation/linux/runtime/；macOS：tools/rc2-adaptation/macos/。
- 当前范围：tools/rc2-adaptation/RESULTS.md 与 FINAL-VERIFICATION.json。历史文件中的“未上传”“pending”“尚未复验”只指成文时点。

PUBLIC-SOURCE-ORIGIN.json、SOURCE-EXPORT-MANIFEST.json 和 TRANSFORMS.json 说明新快照出处。新增脱敏仅针对明确的本地维护/扫描脚本模板；这些模板与原执行字节区分，不能将其哈希作为原日志执行输入。被保护的业务捕获与平台运行时字节未改写。生成的 Mac helper 仍保留通用 D: 构建路径标记，此项已披露，并非个人用户路径；未为美化扫描而修改冻结产物。

源码包保留 Git 模式和符号链接载荷，但不含 .git；公共 Git 提交只沿用原公开历史。旧第三方归档与旧 release/ 文件保留为历史，不声称其覆盖当前代码。

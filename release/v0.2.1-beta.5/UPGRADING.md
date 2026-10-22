# 已有用户与更新边界

Beta.5 是基于 DSH 0.2.1-rc.2 的手动全新独立安装分发，不是任意旧版的原位更新器候选。不要解压覆盖旧 SEP/官方 DSH，不复制私人库到新目录来伪造原库身份。原程序、账本、用户插件、会话与凭据应保留并按受控迁移计划另行处理。

公开分发号为 0.2.1-beta.5，内部仍显示已验构建号（如 0.2.1-beta.3-rc2-adapter.1）；这不是降级或重新验收，也不能以内部派生 semver 推断公开更新资格。ASSET-BINDINGS.json 绑定其关系。

RELEASE-MANIFEST.json 的 automaticUpdateEligible 为 false。本轮不生成伪装为自动更新协议的 dsh-sep-update.json；旧更新器可能报告发布元数据不足，而 GitHub 已有可手动下载的 Beta.5。这表示自动候选尚未提供，不应据此显示“已经是最新”。公网下载→原生确认→默认 Electron 自动安装的同次正例仍搁置/not_run。

本次发布不切换维护者的 Windows 日常版。Linux/macOS 预览包也不替换 Windows 日常程序。

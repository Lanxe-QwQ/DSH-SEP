# 公开便携版的可选 4LM 连接

运行文件只有 `four-lm-agent-link.mjs`，导出 `name` 和 `apply`。公开包可以包含该适配器，但干净 Profile 默认不添加它的插件条目。此目录的 `fixtures/` 和测试文件不进入运行包。

该适配器连接用户已安装、已配置好的 4LM；它不安装 4LM，不创建绑定，不提供默认用户身份，不发现私人目录，不捆绑 token、binding 文件或 4LM 程序。4LM 的自动捕获和召回开关继续由外部 4LM 自己执行。

## 明确启用

在当前宿主的受管配置流程中加入适配器，传入如下 `config`。三个占位符均需替换成当前机器上的绝对本地文件路径，不能直接照抄占位符。

```json
{
  "clientModule": "<ABSOLUTE_4LM_ROOT>/agents/local-client.mjs",
  "bindingFile": "<ABSOLUTE_EXISTING_DSH_BINDING_FILE>",
  "scopeModule": "<ABSOLUTE_CURRENT_HOST_DSH_SCOPE_ENTRY>"
}
```

- `clientModule`：现有 4LM 导出 `AgentClient` 和 `reference` 的本地模块。
- `bindingFile`：用户为 DSH 配置的现有 4LM binding JSON 文件。适配器只将该路径传给外部 `AgentClient`，由 4LM 验证并读取；不要将此文件加入发布包。
- `scopeModule`：**当前宿主** `@deepseek-ai/dsh-scope` 的入口文件。安装器应在当前程序依赖中解析它，不能沿用构建机器的绝对路径。

`clientModule` 或 `bindingFile` 缺失时，适配器不加载 4LM，也不注册捕获和召回 hook。两个字段均设置后，三个字段都必须是绝对本地路径。明确配置的模块缺失、无效绑定或连接故障会返回相应错误，不伪装成已召回；外部 `agent_not_enabled` 与 `{ skipped: true }` 按 4LM 原有契约跳过处理。移除插件条目可关闭连接，不会删除外部 4LM 数据。

## 协议及验证范围

边界按 4LM 0.8.13 的 `AgentClient(bindingFile)`、`processTurn({ sessionId, turnId, text })`、`reference(result)`、`close()` 实现。原始 `dsh-plugin.mjs` SHA-256 为 `83d63e090408c08eb6d97b07742e7bbd5cbff0ae4d78c74967c6f378936e3375`，`local-client.mjs` 为 `3830573aac36043a21c87978b79ee934374a113f2f7d0c08b8fc6e972d6d2097`。这些是核对依据，不是运行时依赖或新版兼容承诺。

保留首轮 pre-step 捕获与召回、同消息去重、用户来源过滤、取消检查和旧 prompt hook 的作用域回退。召回文本原样由外部 `reference` 产生，保留候选、虚构与来源信息。消息来源使用 alpha.2 可追加的 `plugin:four-lm-agent-link`。

本测试使用合成外部客户端，以及实际 0.2.3-alpha.2 的 Cordis、scope 与 SEP 追加校验器。测试不打开真实 binding、不访问网络、不调用模型、不创建会话文件。其结果不等于真实私人 4LM 环境已验收。

在此目录运行以下命令；先把两个占位符替换成隔离测试安装的实际路径。测试只向标准输出写入结果。

```powershell
$env:DSH_ALPHA2_PROGRAM = '<ABSOLUTE_ISOLATED_ALPHA2_DSH_PROGRAM>'
& '<ABSOLUTE_NODE_EXECUTABLE>' --test './four-lm-agent-link.test.mjs'
```

预期：13 项通过、0 失败。覆盖未配置、部分配置、路径校验、首轮召回、事件去重、其他来源过滤、4LM 停用/跳过/故障、作用域隔离、重复注入抑制、取消、释放，以及新旧消息来源的实际追加判定。

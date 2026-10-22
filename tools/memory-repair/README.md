> 历史修复阶段记录：本页的“未改main／未发布／未切换日常版／Mac安装器未重建”仅指当时检查点。当前发行与重建验证见 [Beta.5](../../release/v0.2.1-beta.5/RELEASE-NOTES.md)。冻结候选包内同名策略文档保留原审查输入，不用于判断本次发布状态。

# memory-repair.1 源码与复验

当前结果（2026-10-22）：三项修复的 Windows 91/91、WSL2 Linux 87/87、macOS 15.7.9 ARM64 原生68/68均通过，0跳过。Mac当前索引为 [MACOS-VERIFICATION.json](MACOS-VERIFICATION.json)，原 [VERIFICATION.json](VERIFICATION.json) 保留为上传前检查点。仅专用测试分支已推送，未改 main、未发布Release、未切换日常版。上述数量包含重复流程和跨平台相同定义，不能相加当成独立缺陷类型；完整 Mac app/安装器仍未重建或认证。

修复基线：`a69a754d65664af151e0afd9d95cbb32f3c94371`，公开 Beta.4／DSH 0.2.1-rc.2。隔离分支 `codex/sep-memory-fixes-20261021`。本目录不是私人数据导入、日常安装或发布命令。

- 公共实现：`bundle/modules/system-enhancement-package/src/layered-memory.js`、`automatic-layered-memory.js`、`vendor/bm25.js`。
- 实际宿主入口：`bundle/host/layered-memory` 与 `automatic-memory`。origin 清单对公共实现做精确、带次数的重放，保留原有共享预算和可重试关闭适配。
- RC.2 实际分发源码：`tools/rc2-adaptation/candidate`；`MEMORY-REPAIR.json` 列出相对基线的 7 个修复文件及哈希。`CANDIDATE-SOURCE.json` 是当前完整库存；旧库存保存在本目录 `RC2-CANDIDATE-BASELINE.json`，原历史包与历史证据不改写。
- Linux 由 `linux/runtime/bundle-modules.mjs` 从宿主包解析相同候选，不另复制算法。macOS 的 RC.2 capture 也应由相同候选派生，重新封存 capture/程序/签名后才可交付；不能直接修改已封存 app 内部文件。
- 当前策略见 `bundle/MEMORY-REPAIR.md`；当前结果见 `VERIFICATION.json`，历史失败不得计作新通过。

## 固定测试定义与口径

| 组 | 定义数 | 范围 |
| --- | ---: | --- |
| conflicts | 20 | 合法退出、历史悬空、新竞争者、CAS、重复请求、取消及冷/热写失败 |
| tokenizer | 18 | 原例、11种边界、混排、辅助平面、英文数字和固定排序反例 |
| usage | 24 | 90天问句、重复消息、节流、保护、共享依赖、满500及失败一致性 |
| eligibility | 3 | 捕获候选筛选、恢复容量、共享晋升容量 |
| storage | 3 | 同一流程3轮，真实官方 JSON/P2、关闭重开、删除依据、虚拟时间与取消 |
| integration | 5 | 官方 Loader 两项及同一组合流程3轮，Windows 含真实满500目录 |

65=20+18+24+3 为核心定义；storage 与 integration 中的重复轮次不能解释成更多问题类型。Map 夹具的写入故障注入与真实 JSON/P2 证据分别说明。满额集成的批量数据准备仍走 P2 包装的真实表写入；容量操作走生产记忆 API，不冒充500次用户保存请求。

每次执行使用新输出目录；全部计划样本和失败日志保留，补跑单独列出，不覆盖旧结果。测试不是性能评测，不从包含启动、清理或不同输入的耗时推算开销。

## 可复跑命令

准备与指定 DSH RC.2 相符的隔离宿主及依赖，把上述 candidate 安装到该测试宿主的 `node_modules/dsh-sep-bundle`。不要改日常依赖树。Windows 输出放真实 `D:\AIData\ProjectWork\DSH`；WSL 原生输出放 D 盘承载的 ext4；Mac 使用 `RUNNER_TEMP`。

```powershell
$env:SEP_OFFICIAL_HARNESS = 'D:\AIData\ProjectWork\DSH\<隔离宿主>'
$env:SEP_MEMORY_BUNDLE = "$env:SEP_OFFICIAL_HARNESS\node_modules\dsh-sep-bundle\bundle"
node tools/memory-repair/run.mjs core 'D:\AIData\ProjectWork\DSH\<新核心输出目录>'
node tools/memory-repair/run.mjs storage 'D:\AIData\ProjectWork\DSH\<新存储输出目录>'
node tools/memory-repair/run.mjs integration 'D:\AIData\ProjectWork\DSH\<新Loader输出目录>'
```

Linux/macOS 可用相同 core/storage 命令与 POSIX 绝对路径；integration 使用 Windows 受保护 Profile，不用它证明其他平台完整 Profile。真实模型、私人库和网络密钥均不需要。运行器删除子进程环境中的模型密钥并固定输入哈希，输出 `INPUTS.json`、原始 TAP 日志和 `RESULT.json`。

Git 的 `core.autocrlf` 应为 false，防止克隆改变已钉扎源码字节。应验证原始字节哈希与 origin 重放，不能把重新计算错误字节的哈希当作修复。

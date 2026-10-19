# RC.2 输入与复验导航

本目录是特定版本的隔离适配，不是对未知 DSH 版本通用的安装器。
输入固定为官方 `dsh-v0.2.1-rc.2`，提交
`687f282e8625c6b8d11ff58211a90524be2e4317`。内部 SEP 版本
`0.2.1-beta.3-rc2-adapter.1` 不作为未来公开更新器的版本排序依据。
公开 Beta 版本号需在发布阶段另行分配。当前不发布、不切换日常版。

## 公共输入

1. `candidate/` 是实际 445 文件输入；`CANDIDATE-SOURCE.json` 逐文件绑定。
   根 package 和旧 bundle 是历史输入，不用于打当前包。
2. `derive-runtime.mjs <真实D盘stage> <candidate-source-replay-rN>` 从固定
   444 文件 baseline 派生。stage 必须具备原始 `baseline-runtime`、
   `evidence/INPUTS.json`、`BASELINE-RUNTIME.json` 和精确 `host-rc2`。
   该脚本不下载来源、不覆盖既有输出。历史重放已核对445文件全部一致。
3. `desktop-source-overlay.zip` 是359文件源码覆盖包，先还原固定官方源码，
   再按 `DESKTOP-SOURCE-CAPTURE.json` 覆盖并逐文件核对；不能用于任意宿主。
4. 完整平台依赖由各 builder/锁文件绑定。不要复制私人配置、账本或凭据来
   满足测试。全新安装与已有私人库接续是不同的验收项目。

## 平台入口

- Windows：`build/build-integrated-desktop.mjs`、
  `build/build-integrated-client.mjs` 和 `build/materialize-windows.mjs`；
  `operators/` 保留本机一次性装配步骤，包含固定实验路径，输出经常排他创建，
  不可盲目重跑。`windows-verification/install-archives.mjs <SPEC.json>`
  核验精确归档并全新安装；SPEC 的目标必须是新的真实 D 盘目录。
  安装阶段本身不启动 Host/Electron，桌面验证由单独 probe 完成。
- Linux：产品入口在 `linux/runtime/`；按已安装的固定 manifest 运行，使用
  hash-pinned bwrap、flock、受控工作副本。Wayland 复验契约在
  `linux/wayland/REPRODUCTION.md`；测试必须使用隔离 compositor，不能对真实
  日常桌面注入输入。最终 tar 的源字节与运行测试代次的文件模式分别对账。
- macOS：`macos/build-workflow-r9.yml` 保留应用构建，
  `macos/namespace-build-workflow-r12.yml` 保留修正安装器的构建，
  `.github/workflows/sep-rc2-macos.yml` 为精确修正版的独立原生安装验证。
  安装器只封装固定已验应用，不能把 R9 旧安装器替代修正版。
  `installer-validation/installer-pins.json` 同时固定应用、安装器、源清单。

## 测试与证据

共同核心测试读取 `SEP_OFFICIAL_HARNESS` 指向的精确装有候选的 host，
`SEP_BUNDLE_TEST_ROOT` 指向新的隔离目录。测试使用真实 Loader/存储和合成模型；
`tests/CURRENT-INPUTS.json` 仅是当前字节索引。实际执行日志、当代输入快照、
包指纹与结果必须一起检查，不能用当前索引追认历史执行。

Mac 原生验证先核对下载对象、大小、摘要与所有成员，再恢复、验签、做原生控件
与已安装应用启动验证；测试替换主入口只发生在新复制的测试安装器中，原包不变。
现存 RC.2 资料拒绝路径另外用生产 helper 验证，不由空白安装正例推断。

结果与范围见 `RESULTS.md`。本轮所有实际包和原始证据根为
`D:\AIData\ProjectWork\DSH\rc2-adaptation-20261018-r1`。
完整源码恢复检查点、执行证据索引和当前源码字节索引各自有独立用途。

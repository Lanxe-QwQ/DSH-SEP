# Windows x64 · DSH SEP 0.2.1-beta.4

宿主固定为 DSH `0.2.1-rc.2`，SEP 为 Beta。Full / Only 保留 `RC2-preview-r3` 的原包字节；校验见 [ASSET-BINDINGS.json](ASSET-BINDINGS.json)。

## 安装

Full 包含固定 DSH、SEP、宿主适配与运行支持。Only 不包含完整 DSH，需要包内 `docs/ONLY-SOURCE.md` 指定的精确官方 RC.2 npm 展开来源，并逐文件校验；它不是向任意官方桌面目录安装的插件，也不是通用仓库链接安装。

完整解压到真实本地目录；目标父目录须已存在，目标目录须不存在。不要使用联接、符号链接或别名。按包内 README 和 Only 来源说明操作，示例：

```powershell
# Full
.\runtime\node\node.exe .\installer.mjs --destination 'D:\DSH-SEP-Full'
# Only：先准备精确 RC.2 来源，不能指向任意官方 ASAR
.\runtime\node\node.exe .\installer.mjs --destination 'D:\DSH-SEP-Only' --host-root 'D:\Official-DSH-RC2'
```

安装后双击目标目录 `start.vbs`，按界面配置自己的 API Key；不要重新分发填写后的 `.env`。关闭窗口可保留后台，结束实例请从托盘退出。不要按 Electron/Node 进程名称批量终止。安装器只创建新独立实例，不覆盖已有官方 DSH / SEP 或迁移私人资料；中断现场应保留，不删事务标记强行启动。

## 本轮验证与限制

最终 Full/Only ZIP 的全新安装、拒绝覆盖、篡改拒绝、已安装 Node/pnpm/Python 冒烟通过（fresh-final-r4）。两个独立宿主并发、账本/设置隔离通过；Full/Only 各两轮桌面核心循环通过。

桌面汇总仍为 **blocked**、核心项为 pass：本机执行策略拒绝直接运行未签名 `start.ps1`，没有改系统策略或以其他入口重试来将该项改写为通过。标准 VBS 路径另有证据；其既有子进程参数不等于修改系统持久策略。企业策略也可能限制 VBS。首次无观察启动、物理托盘/首次关闭、异步 VBS 后代独立追踪仍 not_run。可选日常入口指纹列表为空，日常快照守卫 not_run；不宣称本轮验证了日常目录前后指纹。

付费模型、全部用户插件、外部 Computer Use/MCP/WSL/Docker、现有私人库接续和公网自动安装闭环未在本轮完整认证。普通本机 Shell 不获得全面 OS 沙箱保证。脱敏扫描是规定模式的检查，不是任意内容均无秘密的绝对保证。

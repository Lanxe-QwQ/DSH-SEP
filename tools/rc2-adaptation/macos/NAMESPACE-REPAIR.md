> 最终状态：修正版精确ZIP的独立原生安装验证已通过，源5104acfb、run39135657506。
> 真实持久计划绑定RC.2目录、6项固定断言和安装后两轮冷启/正常退出通过。
> 成功路径cleanup为空，不依赖强杀或后续测试清理。以下保留准备阶段的历史说明，
> 其中pending仅描述当时状态；现行结果见FINAL-VERIFICATION.json。

> Current follow-up: native original-miss/detection/preview-refusal checks all passed, including no target/journal writes and unchanged synthetic state. Corrected installer build/signature/archive restore passed on source fecf8489. New installer SHA-256 `1c3a62ae966fe21b58e9ee6a63841cd5e9a30b8415e292b5008dec03b9941a77`, 862171913 bytes, wraps the unchanged R9 application. Its independently reviewed pins are committed for the next fresh Mac installation run; that run is pending at this commit. Preparation-time statements below remain historical.

# RC.2 installer namespace follow-up

The R9 application correctly uses `rc2-mac-finder-preview`, but the R9 installer
account helper and upper controller still inspected `alpha2-mac-finder-preview`.
An empty-account successful installation cannot establish correct protection of
an existing current RC.2 library. Therefore R9 installer `bd331610...` is superseded
for final delivery even if its empty-account UI test passes. The R9 application
and its 103+46/LaunchServices evidence remain fixed and unchanged.

The exact two-source port changes account-native.c twice and controller-core.mjs
once, with frozen input hashes. Three portable regressions passed after a retained
red. Native CI must reproduce the legacy helper miss and prove detection plus
SEP_INSTALLER_DATA_EXISTS rejection before creating a target or transaction, using
actual production helpers without a test-home macro. Synthetic state is removed
only by identity-checked unlink/rmdir of the sentinel and empty test directories.

Only after those checks may a new installer be compiled around the exact fixed
application. The eleven production UI sources, publication/signature checks and
helper safety mechanisms remain; the account helper/controller changes are
explicitly recorded. Installer build budget is 45 minutes to accommodate the
observed 29.7-minute R9 build; this is not a runtime-performance metric or a
relaxation of integrity/cleanup assertions. A separately pinned fresh-install test
is required for the new installer. Native checks/build are pending at commit time.

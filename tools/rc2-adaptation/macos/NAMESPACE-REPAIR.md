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

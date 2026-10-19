> Current RC.2 follow-up: the source contract explicitly ports three files (program DSH gate, native account directory twice, controller directory once). The test-native main directory checks and journal plan directory assertions now use the same RC.2 application namespace. Fixed new installer 1c3a62ae... replaces R9 installer bd331610...; the R9 application is unchanged. Native guard checks passed; this commit admits a new, still-pending fresh installer run.

# RC.2 independent native installer verification

This successor keeps the historical Alpha.2 operators unchanged in Git. The
actual original installer is opened and normally closed first. A separately
copied test application uses the exact audited production native modules and
real NSButton/NSAlert controls to install the fixed payload. Finally the installed
product is opened and normally closed twice through LaunchServices.

The same-job builder receipt is not installation authority. Program and outer
Actions transport pins are recorded only after independent download/hash and
receipt review, then committed before a fresh Mac runner is admitted. The exact
85 production runtime mappings, postbuild 46 definitions and two app cycles are
bound to that prior-run application. A successful input reconstruction is not a
native test result. The original inventory/signature is rechecked after the test.

No physical input, Developer ID/notarization, private-library adoption, production
automatic updater, global process census, or public Mac certification is claimed.
An uncertain cleanup stays blocked and any later CI teardown is attributed
separately. The one startup data-domain change is `alpha2-mac-finder-preview` to
`rc2-mac-finder-preview`; the historical CFBundleIdentifier remains unchanged.

All original source identity, artifact membership, streaming size/hash limits,
no-follow reads, account inventory, explicit confirmation journal, signature,
native source equality and normal-exit assertions remain mandatory.

# DSH SEP 0.2.2-beta.1 for Windows x64

DSH SEP adds project memory and retrieval, budget tracking, guarded file changes, and recovery to DeepSeek Harness. This Beta uses DSH 0.2.3-alpha.2. It restores the SEP wordmark and supports Alpha.2 session writes when the optional 4LM connector returns a memory.

## Install an independent instance

Extract the ZIP, open PowerShell in the extracted directory, and choose a fresh installation path whose parent exists.

```powershell
.\runtime\node\node.exe .\installer.mjs --destination D:\Apps\DSH-SEP-Beta
```

Full includes the DSH program. For Only, add `--host-root` with the exact official 0.2.3-alpha.2 program extracted as described below. The installer verifies each source file it needs and copies it into the new instance. Keep existing DSH and SEP installations in their own directories.

Open `start.vbs` in the installed directory. The instance creates its own workspace, empty session and memory stores, and a fresh consumption ledger. To use a model, configure the provider in the application or fill in the instance’s local `.env`. To shut down the host, use **Application → Exit** or the tray menu. The **Close** control is designed to keep the desktop running in the background.

4LM is optional and absent from a fresh profile. To connect a compatible external 4LM installation, follow [the connector setup](docs/4LM.md). The package contains the adapter and relies on the installed 4LM client for its local recall service.

## Prepare the official source for Only

Use Windows x64 DSH 0.2.3-alpha.2 from the [official fixed download](https://download.deepseek.com/dsh-desk/bin/win-x64/deepseek-harness-0.2.3-alpha.2-win-x64.exe). Its SHA-512 is `caa673445b306fbf50b9825492ad9d546593523bab71a6d80eebbecc6bce50d5f83cd2a13cd304aa3ea2b0cb8168d093381d88741d934d1fa409463ba2086141`.

Use the `resources/app.asar` from that official version, with its companion `app.asar.unpacked` directory beside it. Leave the original files in place. The included extractor checks the official program inventory and writes to a new directory.

```powershell
$previous = $env:ELECTRON_RUN_AS_NODE
try {
  $env:ELECTRON_RUN_AS_NODE = '1'
  & .\runtime\desktop\electron.exe .\installer\materialize-official.cjs 'D:\OfficialDSH\resources\app.asar' 'D:\Apps\DSH-Alpha2-Source'
  if ($LASTEXITCODE -ne 0) { throw 'Official source extraction failed.' }
} finally {
  $env:ELECTRON_RUN_AS_NODE = $previous
}
.\runtime\node\node.exe .\installer.mjs --destination D:\Apps\DSH-SEP-Beta --host-root D:\Apps\DSH-Alpha2-Source\dsh
```

This release covers new standalone Windows x64 installations. Existing installations keep their own configuration, credentials, user plugins, session data, and consumption ledger. The internal SEP module still uses its existing adapter version for runtime compatibility. The package manifest and installation receipt record the public release version.

See [third-party notices](THIRD_PARTY_NOTICES.md), [component inventory](docs/COMPONENTS.json), and [build provenance](docs/BUILD.json).

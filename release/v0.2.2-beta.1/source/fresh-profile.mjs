import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { adaptDailyPresets } from './daily-presets.mjs';
import { buildProfileSelection } from './daily-profile.mjs';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
async function save(path, value) {
  const bytes = JSON.stringify(value, null, 2) + '\n';
  await writeFile(path, bytes, { flag: 'wx', mode: 0o600 });
  return sha(bytes);
}

/** Create an isolated profile and state only under the installer's new destination. */
export async function createFreshProfile({ destination, manifest }) {
  const program = join(destination, 'program');
  const home = join(destination, 'home');
  const managed = join(destination, 'managed');
  const workspace = join(destination, 'workspace');
  const project = { id: randomUUID(), root: workspace };
  const roots = { sessions: join(home, 'sessions'), memory: join(destination, 'data/storage'),
    locks: join(destination, 'state/locks'), backups: join(home, 'file-recovery') };
  const budgetPath = join(destination, 'state/budget/budget.json');
  const profileRoot = join(managed, 'profile');
  const savedSourceRoot = join(home, 'saved-cordis-sources');
  const controlRoot = join(destination, 'state/center/control');
  const electronUserData = join(destination, 'state/electron');
  const runtimeUser = join(destination, 'state/user');
  for (const path of [profileRoot, ...Object.values(roots), dirname(budgetPath), savedSourceRoot, join(home, 'profiles'),
    controlRoot, electronUserData, join(runtimeUser, 'temp'), join(runtimeUser, 'roaming'), join(runtimeUser, 'local'), join(workspace, 'knowledge')]) {
    await mkdir(path, { recursive: true });
  }

  const model = 'deepseek-v4-flash';
  const suite = { projects: [{ sources: ['knowledge'], userProfile: 'instance-user' }],
    memoryAutomation: { capture: false, recall: true, model }, modules: { media: false }, vision: { model },
    p1: { enabled: true, model, budgetPath, limitCny: 100, initialSpentCny: 0, timeoutMs: 60_000, maxTokens: 2048,
      standards: [], prework: true, profileLimits: { maxOutputTokens: 32768, maxInputBytes: 2_000_000 } } };
  const defaults = [
    { id: 'fs-sandbox', config: { cwd: workspace, requireRecovery: true,
      recovery: { root: roots.backups, maxFileBytes: 67_108_864, maxTotalBytes: 1_073_741_824, maxEntries: 1000, retentionMs: 2_592_000_000 } } },
    { id: 'cordis-host-runner', config: { persistence: { root: savedSourceRoot, projectRoot: workspace,
      maxVersionBytes: 1_048_576, maxTotalBytes: 16_777_216, maxPlugins: 32, maxVersions: 16, maxPendingFiles: 16 } } },
    { id: 'storage-json', config: { root: roots.memory } },
    { id: 'session-persistence-jsonl', config: { root: roots.sessions, compression: 'none' } },
    { id: 'agent-default-model', config: { provider: 'deepseek-official', model } },
  ];
  const profile = buildProfileSelection({ programRoot: program, project, roots, budgetPath, savedSourceRoot, suite, patches: defaults });
  const require = createRequire(join(program, 'package.json'));
  const { loadOverlayPatches } = await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-app-boot')).href);
  const nativeRows = ['standard', 'cordis', 'minimal', 'ptc'].map(name =>
    loadOverlayPatches('dsh', join(program, 'node_modules/@deepseek-ai/dsh-web-app/presets', name + '.patch.yml'))[0].insert[0]);
  await save(join(profileRoot, 'package.json'), { name: 'dsh-sep-windows-alpha2-profile', private: true, type: 'module',
    dsh: { profile: { bundles: ['@deepseek-ai/dsh-base', '@deepseek-ai/dsh-web-app'] } } });
  await writeFile(join(profileRoot, 'cordis.yml'), '[]\n', { flag: 'wx', mode: 0o600 });
  await save(join(profileRoot, 'cordis.patch.yml'), [...adaptDailyPresets(nativeRows), ...profile.patches]);
  await writeFile(join(home, 'cordis.patch.yml'), '[]\n', { flag: 'wx', mode: 0o600 });

  const bundleRoot = join(program, 'node_modules/dsh-sep-bundle');
  const dailyAdapterRoot = join(program, 'daily-adapter');
  const bindingPaths = [join(bundleRoot, 'package.json'), ...(await readdir(dailyAdapterRoot)).sort().map(name => join(dailyAdapterRoot, name))];
  const bindings = [];
  for (const path of bindingPaths) bindings.push({ path, sha256: sha(await readFile(path)) });
  const selection = { schema: 2, dsh: manifest.hostVersion, sep: manifest.sepVersion, bundleRoot, dailyAdapterRoot,
    nativeCompactionEntryKey: profile.nativeEntryKey, configuration: { runtime: profile.runtime, ui: { enabled: true, requestTimeoutMs: 120_000 } }, bindings };
  const dailySelectionPath = join(managed, 'daily-selection.json');
  const dailySelectionSha256 = await save(dailySelectionPath, selection);
  const desktopPayloadPath = join(managed, 'desktop-payload.json');
  const desktopPayloadSha256 = await save(desktopPayloadPath, manifest.desktop);
  const credentialsPath = join(destination, '.env');
  await writeFile(credentialsPath, '# Fill in locally when needed.\nDEEPSEEK_API_KEY=\n', { flag: 'wx', mode: 0o600 });

  const config = { schema: 1, kind: 'dsh-sep-managed-daily', dailyRoot: destination, releaseRoot: program, graphHash: manifest.graph.sha256,
    nodeExecutable: join(destination, 'runtime/node/node.exe'), home, storageRoot: roots.memory, controlRoot, lockDirectory: roots.locks,
    electronUserData, runtimeUser, credentialsPath, pnpmEntry: join(destination, 'runtime/primary-runtime/dependencies/pnpm/bin/pnpm.mjs'),
    projects: [project], profileRoot, dailySelectionPath, dailySelectionSha256, desktopRuntimeRoot: join(destination, 'runtime/desktop'),
    desktopPayloadPath, desktopPayloadSha256, runtimeDescriptorSha256: manifest.descriptor.sha256 };
  const configPath = join(destination, 'deployment-rc2.json');
  await save(configPath, config);
  const launcherPath = join(destination, 'launch.mjs');
  await writeFile(launcherPath, await readFile(join(destination, 'installer/launch-template.mjs')), { flag: 'wx' });
  await writeFile(join(destination, 'start.ps1'),
    "$ErrorActionPreference = 'Stop'\r\n& (Join-Path $PSScriptRoot 'runtime\\node\\node.exe') (Join-Path $PSScriptRoot 'launch.mjs')\r\nexit $LASTEXITCODE\r\n",
    { flag: 'wx' });
  await writeFile(join(destination, 'start.vbs'), [
    'Set shell = CreateObject("WScript.Shell")',
    'Set files = CreateObject("Scripting.FileSystemObject")',
    'root = files.GetParentFolderName(WScript.ScriptFullName)',
    'command = Chr(34) & root & "\\runtime\\node\\node.exe" & Chr(34) & " " & Chr(34) & root & "\\launch.mjs" & Chr(34)',
    'result = shell.Run(command, 0, True)',
    'If result <> 0 Then MsgBox "DSH SEP exited with code " & result & ". Run start.ps1 to see the diagnostic.", 48, "DSH SEP"',
    '',
  ].join('\r\n'), { flag: 'wx' });
  return { config, configPath, budgetPath, launcherPath, managedLauncherPath: join(managed, 'bootstrap/launcher.mjs') };
}

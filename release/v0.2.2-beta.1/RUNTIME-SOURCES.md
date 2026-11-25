# Windows x64 运行时来源与第三方许可

本说明记录适配 DeepSeek Harness 0.2.3-alpha.2 时核对过的上游来源。发布清单应把实际装入 Full 和 Only 的文件分别绑定到这些来源及各自的文件哈希。

| 组件 | 固定版本与来源 | 分发材料 |
| --- | --- | --- |
| DeepSeek Harness | 0.2.3-alpha.2，提交 4b399c39a6d1479cd84ca591b4d7c88e24d38a96。[官方源代码](https://github.com/deepseek-ai/deepseek-harness/tree/dsh-v0.2.3-alpha.2) | 保留 DeepSeek 的 MIT 版权和许可，并提供 SEP 对宿主的修改及重建方式。[上游许可](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.3-alpha.2/LICENSE) |
| Electron 与 Chromium | Electron 44.11.5 的 Windows x64 发行包，SHA-256 为 2938040ee81382bb8a99954425a316fee17f23d55f5be0ef413275f7e793c8af。其依赖清单固定 Chromium 152.0.7977.169 和 Node 24.22.3。[Electron 发行包](https://github.com/electron/electron/releases/tag/v44.11.5) · [上游依赖清单](https://github.com/electron/electron/blob/v44.11.5/DEPS) | 保留 Electron 的 LICENSE 和完整的 LICENSES.chromium.html。Chromium 所含组件按各自许可分发。 |
| Node.js 与 pnpm | Windows 独立 Node.js 24.22.3 发行包 SHA-256 为 e612af99f626ab415ea225af6bce5c971feb448cb5cae250bb1c3fa50c5f7d9f。主运行时另含 pnpm 11.28.5。[Node.js 源码与许可](https://github.com/nodejs/node/tree/v24.22.3) · [pnpm 发行记录](https://github.com/pnpm/pnpm/releases/tag/v11.28.5) | 保留 Node LICENSE 所列第三方条款及 pnpm 自带的许可文件。两项运行时各自保留来源与版本记录。 |
| Python | Python Build Standalone 20260901 的 CPython 3.12.14，x86_64-pc-windows-msvc，install_only_stripped，SHA-256 为 7c45c9622400d578709a9b2cddbe8124cc21d382409d9f13406d706d28e31b14。[构建项目发行记录](https://github.com/astral-sh/python-build-standalone/releases/tag/20260901) · [CPython 对应版本](https://www.python.org/downloads/release/python-31214/) · [DSH Windows 运行时锁](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.3-alpha.2/scripts/primary-runtime/lock.json) | 保留 Python 的 LICENSE.txt、随包许可、Wheels 的 *.dist-info 以及 LICENCE 等拼法的文件。按实际运行时清单标注 Wheel 版本。 |
| LibreOffice Kit | Windows x64 0.2.3，MPL-2.0。原生包固定 LibreOffice Core 提交 bce0998afefdbc355585ca324285661a2170ba77。[Kit 源码](https://github.com/deepseek-ai/dsh-libreoffice-kit) · [LibreOffice Core 对应提交](https://github.com/LibreOffice/core/commit/bce0998afefdbc355585ca324285661a2170ba77) | 保留原生包的 sources/ 和 licenses/。sources/core-source.json、core-changes.patch、构建脚本和子依赖清单记录了对应源码和补丁。 |
| sharp 与 libvips | sharp 及 @img/sharp-win32-x64 0.35.5。后者包内版本清单记录 libvips 8.18.7。其许可声明包含 Apache-2.0 和 LGPL-3.0-or-later。[实际 npm 版本记录](https://registry.npmjs.org/@img%2fsharp-win32-x64/0.35.5) · [sharp 源码提交](https://github.com/lovell/sharp/tree/51a990faa26ade5586a4934ac9673c98d8893326) | 保留包内许可和版本清单。按实际装入的二进制核对 libvips、库依赖和对应源代码附件。 |

## FFmpeg 对应源码

Electron 的 Windows 运行时包含 FFmpeg DLL。Chromium 152.0.7977.169 将 FFmpeg 固定在 2b68d2babae73714846961fb0ee47e3b3d2e39a9。Electron 44.11.5 的补丁配置将 patches/ffmpeg 应用于该源码树。对应源码材料需保留这个基础版本、补丁完整序列和该目标构建使用的配置。 [Chromium DEPS](https://raw.githubusercontent.com/chromium/chromium/152.0.7977.169/DEPS) · [FFmpeg 基础源码归档](https://chromium.googlesource.com/chromium/third_party/ffmpeg/+archive/2b68d2babae73714846961fb0ee47e3b3d2e39a9.tar.gz) · [Electron 补丁配置](https://raw.githubusercontent.com/electron/electron/v44.11.5/patches/config.json) · [补丁应用顺序](https://raw.githubusercontent.com/electron/electron/v44.11.5/patches/ffmpeg/.patches) · [FFmpeg 许可说明](https://ffmpeg.org/legal.html)

Electron 的 release.gn 启用 is_component_ffmpeg，实现动态链接。其导入的 all.gn 选择 Chrome 的 FFmpeg 配置并启用 proprietary_codecs。对应源码补充工具校验基础归档的 Git 树以及上游补丁和构建说明的 SHA-256，并在临时源码树上按发布顺序验证补丁应用。 [release.gn](https://raw.githubusercontent.com/electron/electron/v44.11.5/build/args/release.gn) · [all.gn](https://raw.githubusercontent.com/electron/electron/v44.11.5/build/args/all.gn) · [Electron 构建说明](https://www.electronjs.org/docs/latest/development/build-instructions-gn)

通用 Electron 发行包内的 ffmpeg.dll SHA-256 为 797dee858331dd0bbe3cfebdf3f7d3b129927665b780ae2f341ef6e275710dcd。DeepSeek 签名 Windows 供体中的同名 DLL 新增了证书表。核对 Windows PE 的校验和与证书表字段后，两份 DLL 的文件支持的 PE 区域一致。

`DSH-SEP-FFmpeg-Sources-0.2.2-beta.1-Windows-x64.zip` 内的 `SOURCE-RECEIPT.json` 记录 `pass`。基础 Git 树为 `c60e6b597c312801ce91d81110442d40fbf4d672`，Electron 的五个补丁均已按清单顺序应用，发布构建输入也已核对。验证范围止于源码树、补丁应用和构建输入，DLL 重建未执行。该 ZIP 里的早期 `RUNTIME-SOURCES.md` 仍采用准备阶段的措辞，实际核对结果以同一 ZIP 内的 `SOURCE-RECEIPT.json` 为准。 [基础源码提交](https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/2b68d2babae73714846961fb0ee47e3b3d2e39a9) · [五个补丁及顺序](https://raw.githubusercontent.com/electron/electron/v44.11.5/patches/ffmpeg/.patches)

## Windows NumPy、OpenBLAS 与 GCC 运行库

DSH Windows 运行时锁固定了 `numpy-2.3.5-cp312-cp312-win_amd64.whl`，SHA-256 为 `86945f2ee6d10cdfd67bcb4069c1662dd711f7e2a4343db5cecec06b87cf31aa`。NumPy 2.3.5 的构建依赖固定了 `scipy-openblas64==0.3.30.0.7`。已校验 PyPI 的 `scipy_openblas64-0.3.30.0.7-py3-none-win_amd64.whl`，SHA-256 为 `d16734cfa3f0b3390d1cb857bb9175f93475d26e17e47a053657aea8aad902dd`。其中原始 OpenBLAS DLL 的 SHA-256 为 `9e3e5a4229c1ca39f10dc82bba9e2b2bf48037790932566f37aff1a7ccf3588f`，与 Beta.5 Windows 的未签名副本逐字节一致。 [DSH Windows 运行时锁](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.3-alpha.2/scripts/primary-runtime/lock.json) · [NumPy 2.3.5 构建依赖](https://github.com/numpy/numpy/blob/v2.3.5/requirements/ci_requirements.txt) · [PyPI Windows x64 文件及摘要](https://pypi.org/project/scipy-openblas64/0.3.30.0.7/#files)

Full 与 Only 中的 `numpy.libs/libscipy_openblas64_-9e3e5a4229c1ca39f10dc82bba9e2b2b.dll` 和 `numpy-2.3.5.dist-info/LICENSE.txt` 均与签名 DSH Alpha.2 供体逐字节一致，SHA-256 分别为 `a899b3a50bfba442c59e600a9839c6b59e343f9b7d0bb23d97f2f029962f1d52` 和 `596b953e1dcbe829b32ae444387efa15003fc6abdeca8a2179f364a6364c286e`。签名 DLL 比未签名副本新增 10,736 字节的证书表。排除 PE 校验和字段与证书目录字段后，两份 DLL 在证书表之前的字节一致。NumPy 许可证全文记录了 OpenBLAS 的 BSD-3-Clause 许可与其静态链接的 GCC 运行库条款。

OpenBLAS wheel 的构建仓库版本为 MacPython `v0.3.30.0.7`，提交 `2f333bd4a797eb3fbf1aff77668318ff126d351b`。该版本的 Windows x64 配置选择 `UCRT64` 和 `INTERFACE64=1`，使用 `-static -static-libgcc`。脚本显式检出 OpenBLAS `v0.3.30`（提交 `993fad6aebbce34a97d3f8c34d6d79d35b64cc48`），应用 `openblas-make-libs.patch`，并检查链接映射中是否引入静态 `libquadmath`。 [Windows 构建工作流](https://github.com/MacPython/openblas-libs/blob/2f333bd4a797eb3fbf1aff77668318ff126d351b/.github/workflows/windows.yml) · [构建脚本](https://github.com/MacPython/openblas-libs/blob/2f333bd4a797eb3fbf1aff77668318ff126d351b/tools/build_openblas.sh) · [OpenBLAS 补丁](https://github.com/MacPython/openblas-libs/blob/2f333bd4a797eb3fbf1aff77668318ff126d351b/patches-windows/openblas-make-libs.patch) · [OpenBLAS 源码](https://github.com/OpenMathLib/OpenBLAS/tree/993fad6aebbce34a97d3f8c34d6d79d35b64cc48)

工作流固定 Rtools `4.0.0.20220206`。其公开的 2022-02-06 发布归档记录 `mingw-w64-ucrt-x86_64-gcc` 与 `mingw-w64-ucrt-x86_64-gcc-fortran` 均为 `10.3.0-9804`。Rtools 对应配方固定 GCC `10.3.0` 源码归档，SHA-256 为 `64f404c1a650f27fc33da242e1f2df54952e3963a49e06e73f6940f3223ac344`，并记录了构建补丁。核对覆盖 wheel 字节、公开构建配置和 Rtools 发布归档的包版本。原始 CI 的实际编译器调用未取得，GCC 与 OpenBLAS 二进制未重建。 [Rtools 发布归档](https://github.com/r-windows/rtools-installer/releases/tag/2022-02-06) · [Rtools 配方及补丁](https://github.com/r-windows/rtools-testing/tree/c5344cc8c7e310ee4eee513b2381af2e75d65cb9/mingw-w64-gcc) · [GNU GCC 10.3.0 源码归档](https://ftp.gnu.org/gnu/gcc/gcc-10.3.0/gcc-10.3.0.tar.xz)

两份安装包均保留了 NumPy 完整许可通知，涵盖 GPL-3.0-or-later 与 GCC Runtime Library Exception 3.1。适用例外取决于组合目标代码的编译过程是否满足例外条件，以及实际的分发形式。单独分发 GCC 运行库对象代码时，应按 GPLv3 的相应条件提供对应源码。 [GCC 运行库例外正文](https://www.gnu.org/licenses/gcc-exception-3.1.en.html) · [FSF 例外适用问答](https://www.gnu.org/licenses/gcc-exception-3.1-faq.html)

## Windows sharp/libvips 源码附件

上一版发布的 THIRD-PARTY-SOURCES.zip 为 251,343,178 字节，SHA-256 为 237d0644ab6280a6771dc79addd579a95050cb74321c7e5021829069c5cc896b。Alpha.2 Windows 供体的 @img/sharp-win32-x64 许可证和依赖版本清单与 Beta.5 Windows 完整包完全一致。对 libvips-42.dll、libvips-cpp-8.18.7.dll 和 sharp-win32-x64-0.35.5.node 的比较也确认了相同的文件支持 PE 区域，Alpha.2 供体分别新增了证书表。此核对支持沿用附件中对应这三个组件的源代码材料。 [已发布的第三方源码附件](https://github.com/Lanxe-QwQ/DSH-SEP/releases/download/v0.2.1-beta.5/THIRD-PARTY-SOURCES.zip)

## 发布材料核对范围

- 将清单中的组件版本、二进制哈希、许可文件和对应源码入口核对到每份最终 ZIP。对仅 SEP 包，以 ZIP 实际分发的内容为准。若官方运行时由用户另行提供，安装说明应指向固定供体版本和校验值。
- FFmpeg 源码附件与安装包配套发布，补丁应用和构建输入的验证见附件回执。
- 对 LibreOffice 保留实际随包的 Core 提交、补丁及依赖记录。

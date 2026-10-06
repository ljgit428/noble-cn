# Noble – Simplified Chinese Localization (Noble Demo)

[中文](README.md)

A fan-made Simplified Chinese localization patch for the Steam demo of **Noble** by Extra Nice (**Noble Demo, Unity 2022.3 / Mono, Windows x64**), plus the tools and technical notes used to make it.

![title](docs/img/menu.jpg)

## Download

Grab it from **[Releases](https://github.com/ljgit428/noble-cn/releases)**. Two editions:

| Archive | Contents | For |
|---|---|---|
| `Noble_CN_Patch_vX_Installer.zip` | xdelta diffs + `Install.bat` / `Uninstall.bat`. **Ships no original or modified game files**; the installer verifies every MD5 and generates the patched files locally from your own copy. Stops if the version does not match | Recommended |
| `Noble_CN_Patch_vX_Overwrite.zip` | Fully patched files – extract into the game root and overwrite; no version check | Quick & dirty, when you know the build matches |

Supported game build: **0.10.0.189 WINDOWS DEMO** (bottom-left of the title screen). After a game update the patch needs to be re-made.

The first launch after installing takes a few extra seconds (BepInEx init + CJK atlas generation).

## Coverage

- Event titles / descriptions / outcomes (~11k strings), UI, tutorial, titles, house info & backstories, trust / reputation levels, stats & tags, game-over screens
- Hard-coded UI strings in the game DLLs (year counter, confirm dialogs, save / load, succession, house statistics …)
- Names are transliterated; titles and place names are translated
- **Intentionally left in English**: credits and Patreon supporter names, the studio name Extra Nice

Known issues:
- A few code-concatenated fragments (e.g. "or higher" in stat requirements) may still show English
- Chinese is shorter than English, so some buttons / long lines look a bit loose

## Legal

- Noble, its text, code and assets are © **Extra Nice**. This is a free, unofficial fan patch – please buy / download the game legitimately.
- **This repository contains only our own tool code, scripts and notes. It contains no game files, no game text (neither English source nor Chinese translation), no decompiled code and no patched files.**
- Code is MIT licensed (see `LICENSE`). The CJK font is Source Han Sans CN (Adobe, SIL OFL 1.1).

## How it works

1. **Asset-level translation** – [AssetsTools.NET](https://github.com/nesrak1/AssetsTools.NET) + Mono.Cecil rebuild the MonoBehaviour type trees from `Managed\*.dll` (the game ships without type trees); translated strings are written straight back into MonoBehaviour string fields in `level0/1/2`, `resources.assets`, `sharedassets0/1.assets`.
2. **CJK font** – Source Han Sans is embedded into the `LiberationSans` Font asset (PathID 147) in `resources.assets`; the BepInEx plugin `NobleCN.FontFix` then calls `TMP_FontAsset.CreateFontAsset(...)` at runtime to build a 2048×2048 dynamic SDF font and registers it as a global fallback for every TMP font.
3. **DLL strings** – Mono.Cecil replaces user strings in `Noble.Core / Gameplay / UI / ScreenTitle.dll` from a mapping table.
4. **Release** – xdelta3 diffs + MD5 manifest; the installer verifies → backs up to `Noble_Data\_cn_backup` → patches → installs BepInEx and the plugin.

Pitfalls and lessons learned are in [docs/status.md](docs/status.md) (section 5) and [docs/dev-notes.md](docs/dev-notes.md) (Chinese).

## Repository layout

```
install.ps1 / restore.ps1     dev use: install build artifacts from work\ into the game / restore from backup\
tools/
  NobleCN.Tools/              noblecn.exe (.NET 8): dump / apply / set-font / set-field / get-field / dll-strings / dll-apply
  build.bat                   one-shot rebuild: refresh originals → apply translations → inject font → patch DLLs → verify
  build_release.py            builds the Installer and Overwrite release archives
  release/                    install / uninstall scripts and READMEs shipped in the archives
  fetch_deps.ps1              downloads BepInEx 5.4.23.5, xdelta3 3.1.0 and Source Han Sans (not committed)
  fonts/                      font LICENSE (the font itself is fetched by fetch_deps.ps1)
  *.ps1 / *.py / *.bat        assorted screenshot / click / verify / analysis scripts
  scratch/                    early merge / scan scripts
plugin/NobleCN.FontFix/       BepInEx plugin source (Harmony + TextMeshPro)
docs/                         status, dev log, screenshots
```

Not committed (`.gitignore`): `backup/` (original game files), `work/` (dumps, translations, build output), `release_build/`, every `.assets / .dll / .zip / .otf`.

## Building

Requirements: Windows 10/11, .NET SDK 8+, Python 3.10+, Steam Noble Demo.

```bat
:: 0) dependencies
powershell -ExecutionPolicy Bypass -File tools\fetch_deps.ps1
cd tools\NobleCN.Tools && dotnet build -c Release && cd ..\..
cd plugin\NobleCN.FontFix && dotnet build -c Release && cd ..\..   :: adjust GameManaged / BepInExCore in the csproj

:: 1) copy the 6 original asset files to backup\original\ and the 4 DLLs to backup\original_dll\
:: 2) provide translations (not in this repo): work\patch\apply_input.json / apply_final.json / apply_missing.json
::    each entry {"file","pathId","field","cls","text"}; DLL map work\trans2\dll_map.json {"English": "中文"}
:: 3) build + install + verify
tools\build.bat
powershell -ExecutionPolicy Bypass -File install.ps1

:: 4) release archives
python tools\build_release.py v0.1
```

## Credits

Noble © Extra Nice.
[AssetsTools.NET](https://github.com/nesrak1/AssetsTools.NET), [UABEA](https://github.com/nesrak1/UABEA) (classdata.tpk), [BepInEx](https://github.com/BepInEx/BepInEx), [HarmonyX](https://github.com/BepInEx/HarmonyX), [xdelta](https://github.com/jmacd/xdelta), [Source Han Sans](https://github.com/adobe-fonts/source-han-sans).

## ❤️ Support

This patch is free and open source, made purely out of love for the game. If it improved your experience, you can buy the author a coffee ☕ on [Afdian](https://afdian.com/a/yukikaze_studio).

Noble Demo - Simplified Chinese Localization Patch  v0.1
=========================================================

Target: Steam "Noble Demo", in-game version 0.10.0.189 WINDOWS DEMO (Unity 2022.3 / Mono, Windows x64).
The installer verifies the MD5 of every file first; if your build differs it stops without touching anything.

Install:
  1. Close the game.
  2. Double-click "Install.bat" and confirm the game folder (usually auto-detected).
  3. Launch the game - it is now in Simplified Chinese. The first launch takes a few extra seconds
     (BepInEx init + building the CJK font atlas).

Uninstall:
  Double-click "Uninstall.bat" - restores originals from Noble_Data\_cn_backup and removes the font plugin.
  Alternatively use Steam "Verify integrity of game files" (then delete the BepInEx folder manually).

What is inside:
  files\*.xdelta            binary diffs for 6 asset files + 4 game DLLs. NO original or modified game
                            files are shipped - the patched files are generated locally from your own copy.
  files\manifest.txt        original / patched MD5 for every file
  files\xdelta3.exe         xdelta 3.1.0 (open source)
  files\BepInEx_win_x64.zip BepInEx 5 (Unity plugin framework, LGPL)
  files\NobleCN.FontFix.dll our own plugin: registers a CJK TextMeshPro fallback font at runtime
  Font: Source Han Sans CN Regular (Adobe, SIL Open Font License 1.1), embedded via the resources.assets
        diff; license in files\LICENSE-SourceHanSans.txt

Coverage:
  All player-visible text (~10,000 strings): event titles/descriptions/outcomes, UI, tutorial, titles,
  house info, reputation levels, game-over screens and hard-coded UI strings in the game DLLs.
  Intentionally untranslated: credits / Patreon supporter names and the studio name "Extra Nice".

Known issues:
  - A few code-concatenated fragments in stat tooltips (e.g. "or higher") may still show English.
  - Chinese is shorter than English; some buttons / long lines may look slightly loose.
  - After a game update the MD5s change and the installer will refuse to run until the patch is updated.

Legal:
  Noble is (c) Extra Nice. This is a free fan-made patch, not affiliated with the developer.
  No original game files are distributed - only binary diffs, our own plugin and open-source components.

Project / feedback: https://github.com/ljgit428/noble-cn

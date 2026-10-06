Noble Demo - Simplified Chinese Localization Patch  v0.1  (Overwrite edition)
===============================================================================

Target: Steam "Noble Demo", in-game version 0.10.0.189 WINDOWS DEMO.
This edition contains fully patched files and does NOT verify your game version.
If your build differs the game may fail to start - use the Installer edition instead (it checks MD5s).

Install:
  1. Close the game.
  2. Recommended: back up Noble_Data\level0, level1, level2, resources.assets, sharedassets0.assets,
     sharedassets1.assets and Noble_Data\Managed\Noble.Core.dll, Noble.Gameplay.dll,
     Noble.ScreenTitle.dll, Noble.UI.dll.
  3. Extract everything in this archive into the game root (next to Noble.exe), overwrite all.
     Afterwards the folder should contain: Noble_Data\, BepInEx\, winhttp.dll, doorstop_config.ini
  4. Launch the game - it is now in Simplified Chinese. First launch takes a few extra seconds.

Uninstall:
  Steam -> "Verify integrity of game files", then delete the BepInEx folder, winhttp.dll,
  doorstop_config.ini, .doorstop_version and changelog.txt.

Contents:
  Noble_Data\level0 / level1 / level2 / resources.assets / sharedassets0.assets / sharedassets1.assets
      patched assets (translation + Source Han Sans CN Regular font, SIL OFL 1.1)
  Noble_Data\Managed\Noble.Core.dll / Noble.Gameplay.dll / Noble.ScreenTitle.dll / Noble.UI.dll
      game DLLs with hard-coded UI strings translated
  BepInEx\ + winhttp.dll + doorstop_config.ini
      BepInEx 5.4.23.5 (Unity plugin framework, LGPL)
  BepInEx\plugins\NobleCN.FontFix\NobleCN.FontFix.dll
      our own plugin: registers a CJK TextMeshPro fallback font at runtime

Coverage / known issues / legal: see the Installer edition README.
Noble is (c) Extra Nice. Free fan-made patch, not affiliated with the developer.

Project / feedback: https://github.com/ljgit428/noble-cn

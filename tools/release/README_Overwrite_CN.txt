Noble Demo 简体中文汉化补丁  v0.1（直接覆盖版）
=================================================

适用版本：Steam 版《Noble》试玩版（Noble Demo），游戏内版本号 0.10.0.189 WINDOWS DEMO。
          本包是已打好补丁的完整文件，不做版本校验；如果你的游戏版本不同，覆盖后可能无法启动。
          不确定时请改用 Installer 版（会先校验 MD5）。

安装：
  1. 关闭游戏。
  2. 建议先备份游戏目录下的 Noble_Data\level0、level1、level2、resources.assets、
     sharedassets0.assets、sharedassets1.assets 和 Noble_Data\Managed\Noble.Core.dll、
     Noble.Gameplay.dll、Noble.ScreenTitle.dll、Noble.UI.dll。
  3. 把本压缩包内的所有内容解压到游戏根目录（与 Noble.exe 同级），选择"全部覆盖"。
     解压后目录应有：Noble_Data\、BepInEx\、winhttp.dll、doorstop_config.ini
  4. 启动游戏即为简体中文。首次启动会多等几秒（BepInEx 初始化 + 生成中文字体图集）。

卸载：
  在 Steam 中「验证游戏文件完整性」恢复原版，再手动删除 BepInEx 文件夹、winhttp.dll、
  doorstop_config.ini、.doorstop_version、changelog.txt。

包内文件：
  Noble_Data\level0 / level1 / level2 / resources.assets / sharedassets0.assets / sharedassets1.assets
      汉化后的资源文件（含译文 + 思源黑体 Source Han Sans CN Regular，SIL OFL 1.1）
  Noble_Data\Managed\Noble.Core.dll / Noble.Gameplay.dll / Noble.ScreenTitle.dll / Noble.UI.dll
      汉化了硬编码 UI 字符串的游戏 DLL
  BepInEx\ + winhttp.dll + doorstop_config.ini
      BepInEx 5.4.23.5（Unity 插件框架，LGPL）
  BepInEx\plugins\NobleCN.FontFix\NobleCN.FontFix.dll
      本补丁自制的字体插件：运行时为 TextMeshPro 挂上中文字体后备

汉化范围 / 已知问题 / 版权说明：同 Installer 版 README。
《Noble》版权归 Extra Nice 所有，本补丁为玩家自制、免费、与官方无关，请购买/下载正版游玩。

项目主页 / 反馈：https://github.com/ljgit428/noble-cn

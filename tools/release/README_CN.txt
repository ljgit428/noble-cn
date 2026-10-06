Noble Demo 简体中文汉化补丁  v0.1
=====================================

适用版本：Steam 版《Noble》试玩版（Noble Demo），游戏内版本号 0.10.0.189 WINDOWS DEMO
          （Unity 2022.3 / Mono，Windows x64）。安装时会逐个校验文件 MD5，版本不符会直接停止、不改动任何文件。

安装：
  1. 关闭游戏。
  2. 双击「Install.bat」，按提示确认游戏目录（一般会自动找到）。
  3. 启动游戏即为简体中文。首次启动会多等几秒（BepInEx 初始化 + 生成中文字体图集）。

卸载：
  双击「Uninstall.bat」，从 Noble_Data\_cn_backup 恢复原版文件并删除字体插件；
  也可以在 Steam 里「验证游戏文件完整性」恢复原版（BepInEx 目录需手动删除）。

补丁包含什么：
  files\*.xdelta            6 个资源文件 + 4 个游戏 DLL 的二进制差异补丁（不含任何原版/修改后的游戏文件，
                            安装时用你本地的正版文件现场生成）
  files\manifest.txt        每个文件的原版 MD5 / 汉化后 MD5
  files\xdelta3.exe         xdelta 3.1.0（打补丁工具，开源）
  files\BepInEx_win_x64.zip BepInEx 5（Unity 插件框架，LGPL，开源）
  files\NobleCN.FontFix.dll 本补丁自制的字体插件：运行时为 TextMeshPro 挂上中文字体后备，解决缺字
  中文字体：思源黑体 Source Han Sans CN Regular（Adobe，SIL Open Font License 1.1），
            已嵌入 resources.assets 的差异补丁中，LICENSE 见 files\LICENSE-SourceHanSans.txt

汉化范围：
  事件标题/描述/结果、UI、教程、头衔、家族信息、好感等级、游戏结束画面、程序内硬编码的 UI 字符串等
  所有玩家可见文本（约 10,000 条）。有意保留原文：制作名单与 Patreon 赞助者人名、工作室名 Extra Nice。
  人名音译、头衔与地名意译。

已知问题：
  - 部分属性需求提示中的拼接片段（如 "or higher"）由代码拼接，可能偶见英文。
  - 中文比英文短，个别按钮/长句排版可能略有空隙。
  - 游戏更新后 MD5 会变化，补丁将拒绝安装，请等待适配。

版权说明：
  《Noble》版权归 Extra Nice 所有，本补丁为玩家自制、免费、与官方无关，请购买/下载正版游玩。
  本补丁不包含任何原版游戏文件；仅分发差异补丁、自制插件与开源组件。

项目主页 / 反馈：https://github.com/ljgit428/noble-cn

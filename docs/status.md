# Noble 简体中文汉化 — 项目状态

**游戏**：Steam 版 *Noble Demo*（Unity 2022.3.62，Windows x64）
**游戏目录**：`F:\steam\steamapps\common\Noble Demo`
**项目根**：`D:\git\project\Noble CN`

---

## 一、交付方式

1. **资源级汉化**：直接替换 `Noble_Data` 下 6 个资源文件（`.assets` / `level*`），译文以 UTF-8 写入 MonoBehaviour 的字符串字段。
2. **中文字体**：在 `resources.assets` 的 `LiberationSans`（PID 147）里注入 `simhei.ttf` 字体数据；再由 BepInEx 插件在运行时用该字体面生成 TMP 动态字体并挂成全局 fallback。

## 二、当前状态（可玩、已验证）

| 项 | 状态 |
|---|---|
| 术语 + UI 文本（885 条唯一键 → 2,385 条写入） | ✅ 已完成并写入 |
| 家族好感/声望等级标签（信任/戒备/漠然/竭诚效忠…） | ✅ 已完成 |
| 中文字体渲染（标题界面 + 游戏内） | ✅ 正常，无缺字 |
| 安装脚本 / 还原脚本 | ✅ 已做完整往返测试（哈希一致） |
| 事件文本 11,379 条（`b_e_000..047`，约 164 万字符） | ⏳ 未取回、未译 |
| DLL 内字符串（`Years left`、`House `、`Courtship …`） | ⏳ 已 dump（`work/extracted/dll_strings.json`），未译 |
| 底部家族条 `HOUSE SAPWOOD` 等拉丁名/前缀 | ⏳ 待与 DLL 方案一并处理 |
| Credits 赞助者人名 | 有意保留原文 |

## 三、目录结构

```
D:\git\project\Noble CN\
├─ install.ps1 / install.bat        一键安装（备份 + 替换资源 + 装 BepInEx + 装插件）
├─ restore.ps1 / restore.bat        一键还原（可选 -RemoveBepInEx 彻底卸载）
├─ backup\original\                 游戏原始 6 个资源文件（16,354,864 字节）
├─ work\
│   ├─ src\                         每次构建时刷新的原始资源 + globalgamemanagers(.assets) + sharedassets2.assets
│   ├─ build\                       应用译文后的 6 个资源文件（apply.errors.txt 为空）
│   ├─ font\resources.assets        再注入中文字体后的最终 resources.assets（11,122,028 字节）
│   ├─ trans\ trans2\               译文批次、术语表、补充词表
│   ├─ patch\apply_input.json       2,385 条待写入条目
│   └─ extracted\strings.json       全量待译文本（含 11,379 条事件文本）
├─ plugin\NobleCN.FontFix\          BepInEx 插件源码与构建产物
└─ tools\
    ├─ NobleCN.Tools\               noblecn.exe（dump / apply / set-font / set-field / get-field / fields / fonts / dll-strings / dll-apply）
    ├─ build.bat                    一键重建补丁（刷新源 → 应用译文 → 注入字体 → 校验）
    ├─ BepInEx_win_x64_5.4.23.5.zip
    └─ shot2.ps1 / click.ps1        截图与模拟点击（验证用）
```

## 四、构建与验证命令

```bat
:: 重建补丁
D:\git\project\Noble CN\tools\build.bat

:: 安装 / 还原
powershell -ExecutionPolicy Bypass -File "D:\git\project\Noble CN\install.ps1"
powershell -ExecutionPolicy Bypass -File "D:\git\project\Noble CN\restore.ps1"
```

## 五、关键技术要点（踩坑记录）

1. **资源目录必须与 `globalgamemanagers` / `globalgamemanagers.assets` / `sharedassets2.assets` 同目录**，否则 AssetsTools 无法解析脚本类，全部字段变成 dummy（表现为 `Cannot access fields of a dummy field!`，且写入会把资源写坏导致游戏崩溃）。
2. **`vector<uint8>` 字段**（`Font.m_FontData`）在 AssetsTools 中可用 `ByteArray` 布局直接写入，与磁盘格式一致（int32 长度 + 原始字节）。
3. **`m_IsMultiAtlasTexturesEnabled` 是 UInt8**，写 Int32 会破坏资源文件。
4. **TMP 不能在运行时使用系统字体名**：`Font.CreateDynamicFontFromOSFont` 得到的 Font 资源没有内嵌字体数据，`FontEngine.LoadFontFace` 必然失败（"Include Font Data" 报错）。必须让字体数据以**资源**形式存在（本方案注入到 `LiberationSans`）。
5. **不要事后扩容已有 TMP 字体图集**：`m_AtlasWidth/Height` 是只读属性，用反射改字段会与图集纹理/自由矩形不一致，导致字形映射错位（表现为"试→顺"这类错误字）。正确做法是**用 `TMP_FontAsset.CreateFontAsset(font, 62, 6, SDFAA, 2048, 2048, Dynamic, true)` 新建字体资源**，并用 `TryAddCharacters` 探测是否含中文。
6. **BepInEx 插件 MonoBehaviour 会被游戏销毁**（Update 不再触发）→ 改在 `Awake` 里建一个 `DontDestroyOnLoad` 的宿主对象，或在 Harmony 补丁回调里做挂载。
7. Harmony 打 TMP 时 `TextMeshProUGUI.OnEnable` 这类继承方法要用 `AccessTools.Method(type, name)` 直接指定，属性补丁方法名是 `set_text`。
8. **PowerShell 5.1 读取含中文的 `.ps1` 需要 UTF-8 BOM**，否则中文变成乱码导致语法错误。
9. **截图脚本要先 `ShowWindow(hwnd, 9)` 还原最小化的窗口**，否则窗口矩形是 `-32000`。
10. apply 时若目标字段因脚本类未解析而是 dummy，会静默写坏资源 → 已在工具里改为捕获异常并记录到 `apply.errors.txt`（当前为 0 条）。

## 六、后续工作

1. 取回并翻译 11,379 条事件文本（`b_e_000..047`），按现有风格（人名音译、头衔地名意译）统一处理，再跑 `build.bat`。
2. DLL 字符串汉化：`dll_strings.json` 筛选玩家可见项 → 生成映射 → `noblecn dll-apply` → 备份原 DLL 后替换 `Noble_Data\Managed`。
3. 补齐底部家族条的拉丁名与 `House ` 前缀（随 DLL 方案一起）。
4. 排版复查：中文比英文短，个别按钮/长句需要人工看截图微调。

---

## 七、2026-10-06 补译记录（状态更新）

> 本节之前的"二、当前状态 / 六、后续工作"已过时：事件文本 11,379 条与 DLL 字符串（81 条映射）均已完成并安装。

**覆盖率**（解析 `work\extracted\dump_build.json`，排除 m_Name/类型名/路径/GUID/键名等内部字段）：
玩家可见文本 10,383 条，已汉化 9,981 条（**96.1%**）。剩余 402 条全部为有意保留的专名：
Credits 人名 326、Patreon 赞助者 67、核心团队 4 人姓名、工作室名 "Extra Nice"，以及运行时被覆盖的占位文本 "50 BZ - 1100"。

**本次新增**：`work\patch\apply_missing.json`（35 条），已接入 `tools\build.bat` 第 2 步（`apply_input + apply_final + apply_missing`）：
- GameOverReason*.reason ×4（游戏结束原因正文）
- Tag*.staticTitle ×7（ContentCreator / Lowborn / Patreon / Bastard / Fertile / Infamous / Sterile）
- RoleRequirementFlavour.tooltipDescription（rightful heir → 合法继承人）
- OpportunityOutcomeInformation #2897 variants[0].summary
- Credits：Programmer → 程序员、Artist → 美术、subGroup "Interns" → 实习生（×20）

**确认不翻译的字段（勿加入词典）**：
- `OpportunityInformation.references.*.settingAfter`：开发期剧情生成用的提示词上下文（含 "don't make assumptions…" 等 AI 指令）。
  Managed 目录中没有任何 LLM 客户端，且 `GetAfter/settingAfter` 未被 Noble.UI / Gameplay / ScreenTitle 引用 → 玩家不可见。
- `OpportunityInformation.eventType`（accident / affair / trial …）：键名。
- `CreditsGroupCollection.items[].group` 与 `CreditsGroupInformation.groupIdentifier`：分组匹配键（显示用的是 `groupLabel`，已译）。
- `CreditsGroupCollection.items[].subGroup` 中的 Kings / Dukes / Counts：对应 groupIdentifier，显示走 groupLabel（已译）。

**构建/安装结果**：`apply ok: objectsChanged=3760 errors=0`；仅 `sharedassets0.assets` 哈希变化（2F26DCDD），其余 5 个资源与 4 个 DLL 与上一版逐字节相同；已通过 `install.ps1` 安装并哈希校验一致。


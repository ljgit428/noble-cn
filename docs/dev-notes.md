# Noble CN — 汉化项目（工作记录）

## 目标
把 `F:\steam\steamapps\common\Noble Demo`（Unity 2022.3.62 / Mono）汉化为简体中文。

## 环境与通道
- 该 MCP 提供：list_files / read_file / write_file / search_files / run_command（工作区根 = `F:\git\AL_Crosswave_CN_Extract`）
- 已建立沙盒 ←→ 本机文件通道：
  - 上行：`wput.py`（本地文件 → MCP write_file → 拷到目标路径，UTF-8 安全）
  - 下行：`rget2.py`（远端文件 → 拷到 `_bridge\` → MCP read_file）
  - 二进制：`up.py` / `rget.py`（base64 分块）
- 注意：`run_command` **只接受单行命令**（多行会静默失败）；输出含非 ASCII 时可能被吞，需写文件再读。

## 已安装/已构建
- Python 3.10：`UnityPy 1.25.0`（仅用于侦测）
- .NET SDK 10：`D:\git\project\Noble CN\tools\NobleCN.Tools`
  - 依赖：AssetsTools.NET 3.0.5 + AssetsTools.NET.MonoCecil 3.0.4 + `classdata.tpk`（UABEA 仓库）
  - 命令：`noblecn dump <gameDataDir> <out.json>` / `noblecn apply <gameDataDir> <in.json> <outDir>`
  - 作用：用 Managed\*.dll 生成 MonoBehaviour 类型树（游戏本体已剥离类型树），提取/回写字符串字段

## 游戏资源结构（Noble_Data）
- `level0/level1/level2`（3 个场景，含大部分 MonoBehaviour 数据 + UI）
- `resources.assets`、`sharedassets0/1/2.assets`、`globalgamemanagers(.assets)`
- `Managed\Assembly-CSharp.dll` + `Noble.Core/Gameplay/UI/Utilities.dll` 等（文本模板系统：LocalizedTemplateUtility / ILocalizedTemplateProvider / OpportunityLocalizer）
- 字体资源：LiberationSans SDF、PTSansNarrow-Regular/Bold SDF、Courgette-Regular SDF（**均为拉丁字体，无中文字形**）

## 文本盘点（work\extracted\strings.json，31566 条字符串）
| 类别 | 条数 | 说明 |
|---|---|---|
| 需要翻译的散文文本 | **11,966 条 / 1,683,711 字符** | 见下表 |
| 标识符/路径/GUID/数字 | ~19,600 条 | 不翻译 |

主要文本来源：
| 类 | 条数 | 字符 |
|---|---|---|
| OpportunityOutcomeInformation（事件结果：标题/摘要/描述） | 8,759 | 1,606,266 |
| OpportunityInformation（事件说明/通知） | 252 | 15,052 |
| PatreonReward（赞助者奖励说明） | 871 | 16,452 |
| CreditsGroupCollection（制作名单） | 325 | 4,186 |
| RoleRequirementTag / Relation / LifeStage / House（条件描述） | 273 | ~5,363 |
| TextMeshProUGUI / TextMeshPro（UI 文本） | 106 | ~3,035 |
| TodoMessageInformation（引导提示） | 52 | 4,278 |
| AssetIndex / VisualOverrideSchema / TitleManager / Gene / HouseInformation / TagNickname / Phenotype* 等 | ~1,300 | ~9,700 |

占位符形式：`{Main.FirstName}`、`{HouseA}`、`{SideB.FirstName}`；富文本：`<color=green>`、`<b>`、`\n`。

## 待定（需确认）
1. 交付形式：资源替换 / BepInEx 插件 / 两者结合
2. 中文字体方案
3. 翻译范围与节奏（全量 168 万字符 vs 分批）
4. 专名（人名/家族/头衔）翻译风格

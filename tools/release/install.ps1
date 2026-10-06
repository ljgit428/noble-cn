# Noble Demo 简体中文补丁 - 安装 / Noble Demo Simplified Chinese patch - installer
# 流程: 定位游戏 -> 校验原版 MD5 -> 备份 -> xdelta3 打补丁 -> 校验结果 -> 安装 BepInEx + 字体插件
param([string]$Game)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$F = Join-Path $here 'files'
Write-Host '==== Noble Demo 简体中文汉化补丁 安装 / Simplified Chinese patch installer ====' -ForegroundColor Cyan

# 1) 定位游戏目录 / locate game dir
if (-not $Game) {
    $cands = @()
    try {
        $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamPath
        if ($steam) {
            $cands += (Join-Path $steam 'steamapps\common\Noble Demo')
            $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
            if (Test-Path $vdf) {
                Get-Content $vdf | Select-String '"path"\s+"(.+)"' | ForEach-Object {
                    $cands += (Join-Path ($_.Matches[0].Groups[1].Value -replace '\\\\', '\') 'steamapps\common\Noble Demo')
                }
            }
        }
    } catch {}
    foreach ($d in 'C','D','E','F','G') { $cands += "${d}:\steam\steamapps\common\Noble Demo"; $cands += "${d}:\SteamLibrary\steamapps\common\Noble Demo"; $cands += "${d}:\Program Files (x86)\Steam\steamapps\common\Noble Demo" }
    $Game = $cands | Where-Object { Test-Path (Join-Path $_ 'Noble.exe') } | Select-Object -First 1
    $in = Read-Host "游戏目录（含 Noble.exe 的文件夹）/ Game folder containing Noble.exe [回车/Enter = $Game]"
    if ($in) { $Game = $in.Trim('"') }
}
if (-not $Game -or -not (Test-Path (Join-Path $Game 'Noble.exe'))) {
    Write-Host "找不到 Noble.exe / Noble.exe not found: $Game" -ForegroundColor Red; Read-Host '按回车退出 / Press Enter to exit'; exit 1 }
if (Get-Process Noble -ErrorAction SilentlyContinue) { Write-Host '请先关闭游戏 / Please close the game first.' -ForegroundColor Red; Read-Host '按回车退出 / Press Enter'; exit 1 }
Write-Host "游戏目录 / Game: $Game"

# 2) 读取清单并校验 / read manifest, verify MD5
$list = Get-Content (Join-Path $F 'manifest.txt') -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object {
    $a = $_ -split "`t"; [pscustomobject]@{ Rel = $a[0]; Orig = $a[1]; New = $a[2]; Patch = $a[3]; State = '' } }
function MD5($p) { (Get-FileHash -LiteralPath $p -Algorithm MD5).Hash.ToLower() }
$bad = @()
foreach ($x in $list) {
    $p = Join-Path $Game $x.Rel
    if ($x.Orig -eq '-') { $x.State = 'copy'; continue }
    if (-not (Test-Path -LiteralPath $p)) { $bad += "$($x.Rel) (missing)"; continue }
    $h = MD5 $p
    if ($h -eq $x.New) { $x.State = 'done' } elseif ($h -eq $x.Orig) { $x.State = 'todo' } else { $bad += $x.Rel }
}
if ($bad.Count) {
    Write-Host '以下文件与本补丁对应的游戏版本不一致，无法安装：' -ForegroundColor Red
    Write-Host 'These files do not match the game build this patch was made for:' -ForegroundColor Red
    $bad | ForEach-Object { Write-Host "  $_" }
    Write-Host '请在 Steam 中“验证游戏文件完整性”恢复原版后重试；若游戏已更新，请等待补丁适配新版本。'
    Write-Host 'Use Steam "Verify integrity of game files" to restore originals, or wait for a patch update if the game was updated.'
    Read-Host '按回车退出 / Press Enter to exit'; exit 1
}

# 3) 备份 + 打补丁 / backup + patch
$bk = Join-Path $Game 'Noble_Data\_cn_backup'
foreach ($x in $list) {
    $p = Join-Path $Game $x.Rel
    switch ($x.State) {
        'done' { Write-Host "已是汉化版 / already patched: $($x.Rel)" }
        'copy' { New-Item -ItemType Directory -Force -Path (Split-Path $p) | Out-Null; Copy-Item -LiteralPath (Join-Path $F $x.Patch) -Destination $p -Force; Write-Host "复制 / copied: $($x.Rel)" }
        'todo' {
            $b = Join-Path $bk $x.Rel; New-Item -ItemType Directory -Force -Path (Split-Path $b) | Out-Null
            if (-not (Test-Path -LiteralPath $b)) { Copy-Item -LiteralPath $p -Destination $b }
            $tmp = "$p.cn_tmp"
            & (Join-Path $F 'xdelta3.exe') -d -f -s $p (Join-Path $F $x.Patch) $tmp
            if ($LASTEXITCODE -ne 0 -or (MD5 $tmp) -ne $x.New) { Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue; throw "打补丁失败 / patch failed: $($x.Rel)" }
            Move-Item -LiteralPath $tmp -Destination $p -Force
            Write-Host "已汉化 / patched: $($x.Rel)"
        }
    }
}

# 4) BepInEx（中文字体需要运行时插件）/ BepInEx + font plugin
if (Test-Path (Join-Path $Game 'BepInEx\core\BepInEx.dll')) {
    Write-Host 'BepInEx 已存在，跳过 / BepInEx already present, skipped'
} else {
    Expand-Archive -Path (Join-Path $F 'BepInEx_win_x64.zip') -DestinationPath $Game -Force
    Write-Host '已安装 BepInEx 5 / BepInEx 5 installed'
}
$pluginDir = Join-Path $Game 'BepInEx\plugins\NobleCN.FontFix'
New-Item -ItemType Directory -Force -Path $pluginDir | Out-Null
Copy-Item -Force (Join-Path $F 'NobleCN.FontFix.dll') $pluginDir
Write-Host '已安装字体插件 / font plugin installed: BepInEx\plugins\NobleCN.FontFix\NobleCN.FontFix.dll'

Write-Host ''
Write-Host '安装完成！启动游戏即为简体中文。原版文件已备份到 Noble_Data\_cn_backup。' -ForegroundColor Green
Write-Host 'Done! Launch the game to play in Simplified Chinese. Originals backed up to Noble_Data\_cn_backup.' -ForegroundColor Green
Write-Host '首次启动会多等几秒（BepInEx 初始化 + 生成中文字体图集）。/ First launch takes a few extra seconds.'
Read-Host '按回车退出 / Press Enter to exit'

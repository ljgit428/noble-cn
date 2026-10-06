# Noble Demo 简体中文补丁 - 卸载 / uninstaller
# 从 Noble_Data\_cn_backup 恢复原版文件，删除字体插件；可选移除 BepInEx
param([string]$Game)
$ErrorActionPreference = 'Stop'
Write-Host '==== Noble Demo 汉化补丁 卸载（恢复英文原版）/ Uninstall (restore English) ====' -ForegroundColor Cyan
if (-not $Game) {
    $cands = @()
    try { $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamPath; if ($steam) { $cands += (Join-Path $steam 'steamapps\common\Noble Demo') } } catch {}
    foreach ($d in 'C','D','E','F','G') { $cands += "${d}:\steam\steamapps\common\Noble Demo"; $cands += "${d}:\SteamLibrary\steamapps\common\Noble Demo" }
    $Game = $cands | Where-Object { Test-Path (Join-Path $_ 'Noble_Data\_cn_backup') } | Select-Object -First 1
    $in = Read-Host "游戏目录 / Game folder [回车/Enter = $Game]"
    if ($in) { $Game = $in.Trim('"') }
}
if (Get-Process Noble -ErrorAction SilentlyContinue) { Write-Host '请先关闭游戏 / Please close the game first.' -ForegroundColor Red; Read-Host '按回车退出 / Press Enter'; exit 1 }
$bk = Join-Path $Game 'Noble_Data\_cn_backup'
if (-not (Test-Path $bk)) {
    Write-Host "没有找到备份 $bk" -ForegroundColor Red
    Write-Host '可在 Steam 中“验证游戏文件完整性”恢复原版。/ Use Steam "Verify integrity of game files" instead.'
    Read-Host '按回车退出 / Press Enter to exit'; exit 1 }
Get-ChildItem -LiteralPath $bk -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($bk.Length + 1)
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $Game $rel) -Force
    Write-Host "已恢复 / restored: $rel"
}
Remove-Item -LiteralPath $bk -Recurse -Force
$plugin = Join-Path $Game 'BepInEx\plugins\NobleCN.FontFix'
if (Test-Path $plugin) { Remove-Item -LiteralPath $plugin -Recurse -Force; Write-Host '已删除字体插件 / font plugin removed' }
$ans = Read-Host '是否同时移除 BepInEx？(y/N) / Also remove BepInEx? (y/N)'
if ($ans -match '^[Yy]') {
    foreach ($n in @('BepInEx','winhttp.dll','doorstop_config.ini','.doorstop_version','changelog.txt')) {
        $p = Join-Path $Game $n; if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force; Write-Host "已删除 / removed: $n" } }
}
Write-Host '已恢复英文原版。/ English original restored.' -ForegroundColor Green
Read-Host '按回车退出 / Press Enter to exit'

<#
  Noble 简体中文补丁 - 还原脚本
  用法: powershell -ExecutionPolicy Bypass -File restore.ps1 [-GameDir "..."] [-RemoveBepInEx]
  作用: 用 backup\original 与 backup\original_dll 覆盖回原始资源与 DLL；-RemoveBepInEx 时同时卸载 BepInEx 与插件
#>
param(
  [string]$GameDir = "F:\steam\steamapps\common\Noble Demo",
  [switch]$RemoveBepInEx
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataDir = Join-Path $GameDir "Noble_Data"
$managedDir = Join-Path $dataDir "Managed"
$backupDir = Join-Path $root "backup\original"
$backupDllDir = Join-Path $root "backup\original_dll"
$files = @("level0","level1","level2","resources.assets","sharedassets0.assets","sharedassets1.assets")

Write-Host "=== Noble CN 还原 ===" -ForegroundColor Cyan
if (Get-Process Noble -ErrorAction SilentlyContinue) { Write-Host "提示: 游戏正在运行，请先退出。" -ForegroundColor Yellow }

$missing = @()
foreach ($f in $files) { if (-not (Test-Path (Join-Path $backupDir $f))) { $missing += $f } }
if ($missing.Count -gt 0) { throw "备份不完整，缺少: $($missing -join ', ') (在 $backupDir)" }

Write-Host "[1/3] 还原原始资源 ..."
foreach ($f in $files) {
  Copy-Item -Force (Join-Path $backupDir $f) (Join-Path $dataDir $f)
  Write-Host ("      {0,-24} {1,12:N0} bytes" -f $f, (Get-Item (Join-Path $dataDir $f)).Length)
}

Write-Host "[2/3] 还原原始 DLL ..."
$dllBackups = @()
if (Test-Path $backupDllDir) { $dllBackups = Get-ChildItem -Path $backupDllDir -Filter *.dll }
if ($dllBackups.Count -gt 0) {
  foreach ($b in $dllBackups) {
    Copy-Item -Force $b.FullName (Join-Path $managedDir $b.Name)
    Write-Host ("      {0,-24} {1,12:N0} bytes" -f $b.Name, (Get-Item (Join-Path $managedDir $b.Name)).Length)
  }
} else {
  Write-Host "      无 DLL 备份，跳过"
}

if ($RemoveBepInEx) {
  Write-Host "[3/3] 卸载 BepInEx ..."
  Remove-Item -Recurse -Force (Join-Path $GameDir "BepInEx") -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force (Join-Path $GameDir "MonoBleedingEdge") -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $GameDir "winhttp.dll") -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $GameDir "doorstop_config.ini") -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $GameDir ".doorstop_version") -ErrorAction SilentlyContinue
  Remove-Item -Force (Join-Path $GameDir "changelog.txt") -ErrorAction SilentlyContinue
  Write-Host "      BepInEx 已移除"
} else {
  Write-Host "[3/3] 保留 BepInEx（如需彻底卸载请加 -RemoveBepInEx）"
}

Write-Host ""
Write-Host "还原完成，游戏已回到原始英文状态。" -ForegroundColor Green

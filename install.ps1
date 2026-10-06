<#
  Noble 简体中文补丁 - 安装脚本
  用法: powershell -ExecutionPolicy Bypass -File install.ps1 [-GameDir "F:\steam\steamapps\common\Noble Demo"]
  作用: 1) 备份原始资源与原始 DLL  2) 替换 6 个资源文件(译文+中文字体)  3) 替换 4 个文本汉化 DLL  4) 安装 BepInEx 与中文字体插件
#>
param(
  [string]$GameDir = "F:\steam\steamapps\common\Noble Demo"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataDir = Join-Path $GameDir "Noble_Data"
$managedDir = Join-Path $dataDir "Managed"
$backupDir = Join-Path $root "backup\original"
$backupDllDir = Join-Path $root "backup\original_dll"
$files = @("level0","level1","level2","resources.assets","sharedassets0.assets","sharedassets1.assets")

Write-Host "=== Noble CN 安装 ===" -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $GameDir "Noble.exe"))) { throw "找不到游戏: $GameDir\Noble.exe（请用 -GameDir 指定）" }
Write-Host "游戏目录: $GameDir"

# 1) 备份资源
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$needBackup = @()
foreach ($f in $files) { if (-not (Test-Path (Join-Path $backupDir $f))) { $needBackup += $f } }
if ($needBackup.Count -gt 0) {
  Write-Host "[1/5] 备份原始资源 ($($needBackup.Count) 个文件) ..."
  foreach ($f in $needBackup) { Copy-Item -Force (Join-Path $dataDir $f) (Join-Path $backupDir $f) }
} else {
  Write-Host "[1/5] 资源备份已存在，跳过"
}

# 1b) 备份待改的 DLL
$dllSrc = Join-Path $root "work\build_dll"
$dlls = @()
if (Test-Path $dllSrc) { $dlls = Get-ChildItem -Path $dllSrc -Filter *.dll | ForEach-Object { $_.Name } | Sort-Object }
New-Item -ItemType Directory -Force -Path $backupDllDir | Out-Null
$needDll = @()
foreach ($d in $dlls) { if (-not (Test-Path (Join-Path $backupDllDir $d))) { $needDll += $d } }
if ($needDll.Count -gt 0) {
  Write-Host "      备份原始 DLL ($($needDll.Count) 个) ..."
  foreach ($d in $needDll) { Copy-Item -Force (Join-Path $managedDir $d) (Join-Path $backupDllDir $d) }
}

# 2) 替换资源
Write-Host "[2/5] 写入汉化资源 ..."
foreach ($f in $files) {
  $src = Join-Path $root "work\build\$f"
  if ($f -eq "resources.assets") { $src = Join-Path $root "work\font\resources.assets" }   # 含中文字体的版本
  if (-not (Test-Path $src)) { throw "缺少补丁文件: $src" }
  Copy-Item -Force $src (Join-Path $dataDir $f)
  Write-Host ("      {0,-24} {1,12:N0} bytes" -f $f, (Get-Item (Join-Path $dataDir $f)).Length)
}

# 3) 替换文本汉化 DLL
if ($dlls.Count -gt 0) {
  Write-Host "[3/5] 写入 DLL 文本汉化 ($($dlls.Count) 个) ..."
  foreach ($d in $dlls) {
    Copy-Item -Force (Join-Path $dllSrc $d) (Join-Path $managedDir $d)
    Write-Host ("      {0,-24} {1,12:N0} bytes" -f $d, (Get-Item (Join-Path $managedDir $d)).Length)
  }
} else {
  Write-Host "[3/5] 无 DLL 补丁（work\build_dll 为空），跳过"
}

# 4) BepInEx
Write-Host "[4/5] 安装 BepInEx ..."
if (Test-Path (Join-Path $GameDir "BepInEx\core\BepInEx.dll")) {
  Write-Host "      BepInEx 已安装，跳过"
} else {
  $zip = Join-Path $root "tools\BepInEx_win_x64_5.4.23.5.zip"
  if (-not (Test-Path $zip)) { throw "缺少 $zip" }
  Expand-Archive -Path $zip -DestinationPath $GameDir -Force
  Write-Host "      已解压 BepInEx 5.4.23.5 (x64)"
}

# 5) 插件
Write-Host "[5/5] 安装中文字体插件 ..."
$pluginDir = Join-Path $GameDir "BepInEx\plugins\NobleCN.FontFix"
New-Item -ItemType Directory -Force -Path $pluginDir | Out-Null
Copy-Item -Force (Join-Path $root "plugin\NobleCN.FontFix\bin\Release\netstandard2.1\NobleCN.FontFix.dll") $pluginDir
Write-Host "      NobleCN.FontFix.dll -> $pluginDir"

Write-Host ""
Write-Host "安装完成！启动游戏即可看到简体中文。" -ForegroundColor Green
Write-Host "还原方法: powershell -ExecutionPolicy Bypass -File restore.ps1" -ForegroundColor DarkGray

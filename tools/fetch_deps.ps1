# 下载构建 / 发布所需的第三方组件（均不入库）/ fetch third-party deps (not committed)
#   tools\BepInEx_win_x64.zip            BepInEx 5.4.23.5 (LGPL)
#   tools\xdelta3\xdelta3.exe            xdelta 3.1.0 (GPL / Apache-2.0)
#   tools\fonts\SourceHanSansCN-Regular.otf  Source Han Sans CN Regular 2.005R (SIL OFL 1.1)
$ErrorActionPreference = 'Stop'
$tools = Split-Path -Parent $MyInvocation.MyCommand.Path
$tmp = Join-Path $tools '_dl'; New-Item -ItemType Directory -Force $tmp | Out-Null
function Get($u, $o) { if (Test-Path $o) { Write-Host "exists: $o"; return }; Write-Host "downloading $u"; curl.exe -L --retry 5 -sS -o $o $u; if ($LASTEXITCODE) { throw "download failed: $u" } }
Add-Type -AssemblyName System.IO.Compression.FileSystem

Get 'https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_win_x64_5.4.23.5.zip' (Join-Path $tools 'BepInEx_win_x64.zip')

$xz = Join-Path $tmp 'xdelta3.zip'
Get 'https://github.com/jmacd/xdelta-gpl/releases/download/v3.1.0/xdelta3-3.1.0-x86_64.exe.zip' $xz
New-Item -ItemType Directory -Force (Join-Path $tools 'xdelta3') | Out-Null
$z = [IO.Compression.ZipFile]::OpenRead($xz)
$e = $z.Entries | Where-Object { $_.Name -like '*.exe' } | Select-Object -First 1
[IO.Compression.ZipFileExtensions]::ExtractToFile($e, (Join-Path $tools 'xdelta3\xdelta3.exe'), $true); $z.Dispose()

$fz = Join-Path $tmp 'SourceHanSansCN.zip'
Get 'https://github.com/adobe-fonts/source-han-sans/releases/download/2.005R/19_SourceHanSansCN.zip' $fz
$z = [IO.Compression.ZipFile]::OpenRead($fz)
$e = $z.Entries | Where-Object { $_.Name -eq 'SourceHanSansCN-Regular.otf' } | Select-Object -First 1
[IO.Compression.ZipFileExtensions]::ExtractToFile($e, (Join-Path $tools 'fonts\SourceHanSansCN-Regular.otf'), $true)
$e = $z.Entries | Where-Object { $_.Name -eq 'LICENSE.txt' } | Select-Object -First 1
[IO.Compression.ZipFileExtensions]::ExtractToFile($e, (Join-Path $tools 'fonts\LICENSE-SourceHanSans.txt'), $true); $z.Dispose()
Remove-Item $tmp -Recurse -Force
Write-Host 'done' -ForegroundColor Green

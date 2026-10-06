$root = "D:\git\project\Noble CN"
$game = "F:\steam\steamapps\common\Noble Demo"
$data = Join-Path $game "Noble_Data"
$backup = Join-Path $root "backup\original"
$build = Join-Path $root "work\build"
$font = Join-Path $root "work\font"
$files = @("level0","level1","level2","resources.assets","sharedassets0.assets","sharedassets1.assets")
$o = @()
function HashOf($p) { if (Test-Path $p) { (Get-FileHash -Algorithm MD5 $p).Hash.Substring(0,12) } else { "MISSING" } }
Stop-Process -Name Noble -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$o += "=== RESTORE ==="
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "restore.ps1") *>&1 | ForEach-Object { $o += "  $_" }
foreach ($f in $files) { $o += ("{0,-24} game={1} backup={2} match={3}" -f $f, (HashOf (Join-Path $data $f)), (HashOf (Join-Path $backup $f)), ((HashOf (Join-Path $data $f)) -eq (HashOf (Join-Path $backup $f)))) }
$o += "=== INSTALL ==="
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "install.ps1") *>&1 | ForEach-Object { $o += "  $_" }
foreach ($f in $files) {
  $exp = if ($f -eq "resources.assets") { HashOf (Join-Path $font $f) } else { HashOf (Join-Path $build $f) }
  $o += ("{0,-24} game={1} expected={2} match={3}" -f $f, (HashOf (Join-Path $data $f)), $exp, ((HashOf (Join-Path $data $f)) -eq $exp))
}
$o | Out-File -Encoding utf8 "F:\git\AL_Crosswave_CN_Extract\_bridge\dep2.txt"
'done'

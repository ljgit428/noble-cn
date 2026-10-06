$root = "D:\git\project\Noble CN"
$game = "F:\steam\steamapps\common\Noble Demo"
$data = Join-Path $game "Noble_Data"
$backup = Join-Path $root "backup\original"
$build = Join-Path $root "work\build"
$font = Join-Path $root "work\font"
$files = @("level0","level1","level2","resources.assets","sharedassets0.assets","sharedassets1.assets")
$o = @()
function HashOf($p) { if (Test-Path $p) { (Get-FileHash -Algorithm MD5 $p).Hash.Substring(0,12) } else { "MISSING" } }
$o += "--- before: game vs backup vs build ---"
foreach ($f in $files) { $o += ("{0,-24} game={1} backup={2} build={3} font={4}" -f $f, (HashOf (Join-Path $data $f)), (HashOf (Join-Path $backup $f)), (HashOf (Join-Path $build $f)), (HashOf (Join-Path $font $f))) }
$o | Out-File -Encoding utf8 "F:\git\AL_Crosswave_CN_Extract\_bridge\dep1.txt"
'step1 ok'

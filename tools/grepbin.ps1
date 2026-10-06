$p = 'D:\git\project\Noble CN\work\src\sharedassets0.assets'
$b = [IO.File]::ReadAllBytes($p)
$s16 = [Text.Encoding]::Unicode.GetString($b)
$s8  = [Text.Encoding]::UTF8.GetString($b)
foreach ($needle in @('Have 50 children','Build a castle','Get a Count title','Reach the 6th')) {
  $in16 = $s16.Contains($needle)
  $in8  = $s8.Contains($needle)
  Write-Host ("{0,-22} utf16={1} utf8={2}" -f $needle, $in16, $in8)
}

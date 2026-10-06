$ErrorActionPreference='Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
Add-Type @"
using System;using System.Runtime.InteropServices;
public class WR2 {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$p = Get-Process Noble -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Host 'NO_PROC'; exit 1 }
$r = New-Object WR2+RECT
[void][WR2]::GetWindowRect($p.MainWindowHandle, [ref]$r)
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
$sx = $w / 1280.0; $sy = $h / 720.0
function C([int]$x, [int]$y) {
  [Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
  Start-Sleep -Seconds 1
  & 'D:\git\project\Noble CN\tools\click.ps1' -X ([int]($x * $script:sx)) -Y ([int]($y * $script:sy)) | Out-Null
}
C 110 208
Start-Sleep -Seconds 60
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn11_a.jpg' -MaxWidth 1280 -Quality 76 | Out-Null
Start-Sleep -Seconds 45
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn11_b.jpg' -MaxWidth 1280 -Quality 76 | Out-Null
Start-Sleep -Seconds 45
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn11_c.jpg' -MaxWidth 1280 -Quality 76 | Out-Null
Write-Host 'SHOTDONE11'

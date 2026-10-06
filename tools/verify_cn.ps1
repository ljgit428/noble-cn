$ErrorActionPreference = 'Continue'
Get-Process Noble -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\install.ps1'
Start-Sleep -Seconds 1
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Process 'F:\steam\steamapps\common\Noble Demo\Noble.exe'
Start-Sleep -Seconds 50
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 3
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn_full_01.jpg' -MaxWidth 1280 -Quality 78
Write-Host 'SHOTDONE'

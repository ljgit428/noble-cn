$ErrorActionPreference='Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
Get-Process Noble -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\install.ps1'
Start-Sleep -Seconds 1
Start-Process 'F:\steam\steamapps\common\Noble Demo\Noble.exe'
Start-Sleep -Seconds 45
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\click.ps1' -X 637 -Y 460 | Out-Null
Start-Sleep -Seconds 30
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 958 -Y 720 | Out-Null
Start-Sleep -Seconds 28
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 3
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\mn_1.jpg' -MaxWidth 1280 -Quality 78 | Out-Null
Write-Host 'SHOTDONE8'

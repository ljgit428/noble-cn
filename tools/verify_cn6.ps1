$ErrorActionPreference='Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
Get-Process Noble -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process 'F:\steam\steamapps\common\Noble Demo\Noble.exe'
Start-Sleep -Seconds 45
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\t6_1_title.jpg' -MaxWidth 1280 -Quality 78 | Out-Null
& 'D:\git\project\Noble CN\tools\click.ps1' -X 956 -Y 690 | Out-Null
Start-Sleep -Seconds 30
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\t6_2_newgame.jpg' -MaxWidth 1280 -Quality 78 | Out-Null
Write-Host 'SHOTDONE6'

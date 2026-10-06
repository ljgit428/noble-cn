$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\click.ps1' -X 637 -Y 460
Start-Sleep -Seconds 25
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 958 -Y 720
Start-Sleep -Seconds 20
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 3
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn_full_02.jpg' -MaxWidth 1280 -Quality 78
Write-Host 'SHOTDONE2'

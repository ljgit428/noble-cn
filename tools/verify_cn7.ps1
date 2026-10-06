$ErrorActionPreference='Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 637 -Y 460 | Out-Null
Start-Sleep -Seconds 25
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 958 -Y 720 | Out-Null
Start-Sleep -Seconds 30
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\ng_1.jpg' -MaxWidth 1280 -Quality 78 | Out-Null
& 'D:\git\project\Noble CN\tools\click.ps1' -X 183 -Y 441 | Out-Null
Start-Sleep -Seconds 4
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\ng_2.jpg' -MaxWidth 1280 -Quality 78 | Out-Null
Write-Host 'SHOTDONE7'

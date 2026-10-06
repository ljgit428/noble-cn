$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 472 -Y 975
Start-Sleep -Seconds 3
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn_house_info.jpg' -MaxWidth 1280 -Quality 78
Start-Sleep -Seconds 1
& 'D:\git\project\Noble CN\tools\click.ps1' -X 122 -Y 66
Start-Sleep -Seconds 12
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
& 'D:\git\project\Noble CN\tools\shot2.ps1' -Out 'D:\git\project\Noble CN\work\shots\cn_menu.jpg' -MaxWidth 1280 -Quality 78
Write-Host 'SHOTDONE4'

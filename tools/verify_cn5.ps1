$ErrorActionPreference='Continue'
Add-Type -AssemblyName Microsoft.VisualBasic
function Shot($n){ & 'D:\git\project\Noble CN\tools\shot2.ps1' -Out ("D:\git\project\Noble CN\work\shots\v5_{0}.jpg" -f $n) -MaxWidth 1280 -Quality 78 | Out-Null }
function Clk($x,$y){ & 'D:\git\project\Noble CN\tools\click.ps1' -X $x -Y $y | Out-Null }
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 1
Clk 183 99          # 主菜单
Start-Sleep -Seconds 3
Shot a
Clk 800 617         # 是 -> 回标题
Start-Sleep -Seconds 14
Shot b
Clk 957 837         # 删除存档 X
Start-Sleep -Seconds 3
Shot c
Clk 800 617         # 确认删除 是
Start-Sleep -Seconds 4
Shot d
Clk 956 690         # 空槽位 -> 开新游戏
Start-Sleep -Seconds 35
[Microsoft.VisualBasic.Interaction]::AppActivate('Noble') | Out-Null
Start-Sleep -Seconds 2
Shot e
Clk 183 441         # 跳过教程
Start-Sleep -Seconds 3
Shot f
Write-Host 'SHOTDONE5'

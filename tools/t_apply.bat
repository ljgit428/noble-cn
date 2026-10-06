@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\t_apply.log
set MANAGED=F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed
echo == A: apply with explicit managed == > "%B%"
"%TOOL%" apply "D:\git\project\Noble CN\work\src" "D:\git\project\Noble CN\work\patch\apply_input.json" "D:\git\project\Noble CN\work\t1" "%MANAGED%" >> "%B%" 2>&1
echo == B: get-field with explicit managed on src == >> "%B%"
"%TOOL%" get-field "D:\git\project\Noble CN\work\src" level0 2238 m_text "%MANAGED%" >> "%B%" 2>&1
echo == C: get-field on game dir == >> "%B%"
"%TOOL%" get-field "F:\steam\steamapps\common\Noble Demo\Noble_Data" level0 2238 m_text >> "%B%" 2>&1
echo done >> "%B%"

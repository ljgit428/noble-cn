@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\diag2.log
echo --- tpk files --- > "%B%"
dir /s /b "D:\git\project\Noble CN\*.tpk" >> "%B%" 2>&1
echo --- extracted dir --- >> "%B%"
dir /b "D:\git\project\Noble CN\work\extracted" >> "%B%" 2>&1
echo --- get-field on extracted --- >> "%B%"
"%TOOL%" get-field "D:\git\project\Noble CN\work\extracted" level0 2238 m_text >> "%B%" 2>&1
echo --- get-field on game dir --- >> "%B%"
"%TOOL%" get-field "F:\steam\steamapps\common\Noble Demo\Noble_Data" level0 2238 m_text >> "%B%" 2>&1
echo --- get-field on build (new, bad) --- >> "%B%"
"%TOOL%" get-field "D:\git\project\Noble CN\work\build" level0 2238 m_text >> "%B%" 2>&1
echo --- get-field on src --- >> "%B%"
"%TOOL%" get-field "D:\git\project\Noble CN\work\src" level0 2238 m_Name >> "%B%" 2>&1
echo done >> "%B%"

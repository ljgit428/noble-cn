@echo off
setlocal
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set BRIDGE=F:\git\AL_Crosswave_CN_Extract\_bridge
set MANAGED=F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed
if exist "D:\git\project\Noble CN\work\font" rmdir /s /q "D:\git\project\Noble CN\work\font"
"%TOOL%" set-font "D:\git\project\Noble CN\work\build" resources.assets 147 "C:\Windows\Fonts\simhei.ttf" "D:\git\project\Noble CN\work\font" "%MANAGED%" SimHei > "%BRIDGE%\sf5.log" 2>&1
"%TOOL%" get-field "D:\git\project\Noble CN\work\font" level0 2238 m_text >> "%BRIDGE%\sf5.log" 2>&1
"%TOOL%" fields "D:\git\project\Noble CN\work\font" resources.assets 244 >> "%BRIDGE%\sf5.log" 2>&1
dir /b "D:\git\project\Noble CN\work\font" >> "%BRIDGE%\sf5.log" 2>&1
echo DONE >> "%BRIDGE%\sf5.log"

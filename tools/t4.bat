@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\probe.log
set MANAGED=F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed
cd /d "D:\git\project\Noble CN\tools\NobleCN.Tools" 
dotnet build -c Release --nologo > nul 2>&1
echo === SRC (pristine, with ggm.assets) === > "%B%"
"%TOOL%" probe-read "D:\git\project\Noble CN\work\src" level0 2238 m_text "%MANAGED%" >> "%B%" 2>&1
echo === GAME (patched) === >> "%B%"
"%TOOL%" probe-read "F:\steam\steamapps\common\Noble Demo\Noble_Data" level0 2238 m_text >> "%B%" 2>&1

@echo off
setlocal
set ROOT=D:\git\project\Noble CN
set TOOL=%ROOT%\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set BRIDGE=F:\git\AL_Crosswave_CN_Extract\_bridge
set GAME=F:\steam\steamapps\common\Noble Demo
set MANAGED=%GAME%\Noble_Data\Managed
set DLLSRC=%ROOT%\backup\original_dll
if not exist "%DLLSRC%\Noble.UI.dll" set DLLSRC=%MANAGED%
set SRC=%ROOT%\work\src
set PATCH=%ROOT%\work\patch

echo [1/6] refresh pristine sources
if exist "%SRC%" rmdir /s /q "%SRC%"
mkdir "%SRC%"
copy /y "%ROOT%\backup\original\*" "%SRC%" > nul
rem 脚本类需要同目录下的 globalgamemanagers(.assets) 才能被解析，直接取游戏中的原件
copy /y "%GAME%\Noble_Data\globalgamemanagers" "%SRC%" > nul
copy /y "%GAME%\Noble_Data\globalgamemanagers.assets" "%SRC%" > nul
copy /y "%GAME%\Noble_Data\sharedassets2.assets" "%SRC%" > nul

echo [2/6] combine patch inputs
powershell -NoProfile -Command "$a=Get-Content -Raw -Encoding UTF8 '%PATCH%\apply_input.json' | ConvertFrom-Json; $b=Get-Content -Raw -Encoding UTF8 '%PATCH%\apply_final.json' | ConvertFrom-Json; $c=Get-Content -Raw -Encoding UTF8 '%PATCH%\apply_missing.json' | ConvertFrom-Json; ($a+$b+$c) | ConvertTo-Json -Depth 8 -Compress | Set-Content -Encoding UTF8 '%PATCH%\apply_combined.json'"

echo [3/6] apply translations + name localization
if exist "%ROOT%\work\build" rmdir /s /q "%ROOT%\work\build"
"%TOOL%" apply "%SRC%" "%PATCH%\apply_combined.json" "%ROOT%\work\build" "%MANAGED%" > "%BRIDGE%\build2.log" 2>&1

echo [4/6] inject CJK font
if exist "%ROOT%\work\font" rmdir /s /q "%ROOT%\work\font"
"%TOOL%" set-font "%ROOT%\work\build" resources.assets 147 "%ROOT%\tools\fonts\SourceHanSansCN-Regular.otf" "%ROOT%\work\font" "%MANAGED%" "Source Han Sans CN" >> "%BRIDGE%\build2.log" 2>&1

echo [5/6] patch managed dll strings
if exist "%ROOT%\work\build_dll" rmdir /s /q "%ROOT%\work\build_dll"
"%TOOL%" dll-apply "%DLLSRC%" "%ROOT%\work\trans2\dll_map.json" "%ROOT%\work\build_dll" >> "%BRIDGE%\build2.log" 2>&1

echo [6/6] verify + error summary
rem 解析脚本类需要同目录下的 globalgamemanagers(.assets)
if not exist "%ROOT%\work\build\globalgamemanagers" copy /y "%GAME%\Noble_Data\globalgamemanagers" "%ROOT%\work\build" > nul
if not exist "%ROOT%\work\build\globalgamemanagers.assets" copy /y "%GAME%\Noble_Data\globalgamemanagers.assets" "%ROOT%\work\build" > nul
"%TOOL%" get-field "%ROOT%\work\font" resources.assets 244 m_Name "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
"%TOOL%" get-field "%ROOT%\work\build" sharedassets0.assets 2281 nameInitial "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
"%TOOL%" get-field "%ROOT%\work\build" sharedassets0.assets 2281 mottoLatin "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
"%TOOL%" get-field "%ROOT%\work\build" sharedassets0.assets 2380 variants.Array[0].summary "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
"%TOOL%" get-field "%ROOT%\work\build" sharedassets0.assets 2308 references.ref:2794093907554336955.notificationDescription "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
"%TOOL%" get-field "%ROOT%\work\build" sharedassets0.assets 4713 title "%MANAGED%" >> "%BRIDGE%\build2.log" 2>&1
if exist "%ROOT%\work\build\apply.errors.txt" (type "%ROOT%\work\build\apply.errors.txt" | find /c /v "") >> "%BRIDGE%\build2.log" 2>&1
type "%BRIDGE%\build2.log"
echo BUILD-DONE

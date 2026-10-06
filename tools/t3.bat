@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\info2.txt
set G=F:\steam\steamapps\common\Noble Demo\Noble_Data
echo === GAME DIR (patched) === > "%B%"
"%TOOL%" info "%G%" >> "%B%" 2>&1
echo === BACKUP (pristine) === >> "%B%"
"%TOOL%" info "D:\git\project\Noble CN\backup\original" >> "%B%" 2>&1
echo === SRC === >> "%B%"
"%TOOL%" info "D:\git\project\Noble CN\work\src" >> "%B%" 2>&1

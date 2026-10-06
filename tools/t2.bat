@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\t2.log
set MANAGED=F:\steam\steamapps\common\Noble Demo\Noble_Data\Managed
echo == hashes == > "%B%"
certutil -hashfile "D:\git\project\Noble CN\backup\original\level0" MD5 | findstr /v ":"
certutil -hashfile "D:\git\project\Noble CN\work\src\level0" MD5 | findstr /v ":" >> "%B%" 2>&1
certutil -hashfile "D:\git\project\Noble CN\work\build\level0" MD5 | findstr /v ":" >> "%B%" 2>&1
echo == read backup == >> "%B%"
"%TOOL%" get-field "D:\git\project\Noble CN\backup\original" level0 2238 m_text "%MANAGED%" >> "%B%" 2>&1
echo == read game == >> "%B%"
"%TOOL%" get-field "F:\steam\steamapps\common\Noble Demo\Noble_Data" level0 2238 m_text >> "%B%" 2>&1
echo == files in backup\original == >> "%B%"
dir /b "D:\git\project\Noble CN\backup\original" >> "%B%" 2>&1
echo done >> "%B%"

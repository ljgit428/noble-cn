@echo off
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\trans.txt
echo === work\trans listing === > "%B%"
dir /b /o-s "D:\git\project\Noble CN\work\trans" >> "%B%" 2>&1
echo === sizes of b_ and e_ and event_ === >> "%B%"
for %%f in ("D:\git\project\Noble CN\work\trans\b_e_*.json") do @echo %%~nxf %%~zf >> "%B%"
type "%B%"

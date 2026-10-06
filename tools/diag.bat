@echo off
set TOOL=D:\git\project\Noble CN\tools\NobleCN.Tools\bin\Release\net8.0\noblecn.exe
set B=F:\git\AL_Crosswave_CN_Extract\_bridge\diag.log
set S=D:\git\project\Noble CN\work\src
echo --- 1: level0:2238 m_text (pristine) --- > "%B%"
"%TOOL%" get-field "%S%" level0 2238 m_text >> "%B%" 2>&1
echo --- 2: level0:2238 m_text full tree sanity --- >> "%B%"
"%TOOL%" fields "%S%" level0 2238 >> "%B%" 2>&1
echo --- 3: sharedassets1:3020 m_AnimationTriggers --- >> "%B%"
"%TOOL%" get-field "%S%" sharedassets1.assets 3020 m_AnimationTriggers >> "%B%" 2>&1
echo --- 4: sharedassets0 HouseStatStages 2289 stages --- >> "%B%"
"%TOOL%" get-field "%S%" sharedassets0.assets 2289 stages >> "%B%" 2>&1
echo done >> "%B%"

@echo off
title Combine regional wind hazard with site exposure multipliers
CALL conda.bat activate tsed

python %CD%\applyMultipliers.py -c %CD%\applyMultipliers.ini
@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              SmartCutElf 打包                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

python scripts\build.py

echo.
pause

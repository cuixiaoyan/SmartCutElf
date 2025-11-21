@echo off
chcp 65001 >nul
cls

echo ╔══════════════════════════════════════════════════════════════╗
echo ║              SmartCutElf 打包工具                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 请选择打包模式：
echo.
echo   1. 快速打包（增量，约10-15秒）  ⚡ 推荐开发使用
echo   2. 完整打包（清理重建，约40秒）  🔧 推荐发布使用
echo.
echo ══════════════════════════════════════════════════════════════
echo.

set /p mode="请输入选项 (1 或 2): "

if "%mode%"=="1" goto fast
if "%mode%"=="2" goto full

echo.
echo ❌ 无效选项，请输入 1 或 2
pause
exit /b

:fast
echo.
echo ⚡ 快速打包模式（跳过清理）
echo ══════════════════════════════════════════════════════════════
echo.
python scripts/build.py --skip-clean
goto end

:full
echo.
echo 🔧 完整打包模式（清理重建）
echo ══════════════════════════════════════════════════════════════
echo.
python scripts/build.py
goto end

:end
echo.
echo ══════════════════════════════════════════════════════════════
pause

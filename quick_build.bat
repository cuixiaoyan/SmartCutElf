@echo off
chcp 65001 >nul
echo ========================================
echo   SmartCutElf 快速打包脚本
echo ========================================
echo.

echo [1/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo   ✓ 清理完成

echo.
echo [2/3] 开始打包...
pyinstaller --name=SmartCutElf --windowed --onefile --clean --noconfirm --add-data="config.yaml;." --add-data="assets;assets" --hidden-import=PyQt5.QtMultimedia --hidden-import=PyQt5.QtMultimediaWidgets --icon=assets/app_icon.ico main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo   ✓ 打包完成

echo.
echo [3/3] 复制配置文件...
copy config.yaml dist\ >nul
copy README.md dist\ >nul
xcopy /E /I /Y assets dist\assets >nul
echo   ✓ 文件复制完成

echo.
echo ========================================
echo   ✨ 打包成功！
echo ========================================
echo.
echo 📁 输出目录: dist\
echo 📦 可执行文件: dist\SmartCutElf.exe
echo.
echo 💡 提示: 可以直接运行 dist\SmartCutElf.exe 测试
echo.
pause

@echo off
echo 清理Python缓存文件...

REM 删除所有 __pycache__ 目录
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM 删除所有 .pyc 文件
del /s /q *.pyc 2>nul

REM 删除所有 .pyo 文件
del /s /q *.pyo 2>nul

echo 缓存清理完成！
echo 请重新启动应用程序。
pause

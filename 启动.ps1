# 快速启动 SmartCutElf
# 这个脚本会帮助您快速启动应用

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SmartCutElf - 智剪精灵 启动脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
Write-Host "检查Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查FFmpeg
Write-Host "检查FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg已安装" -ForegroundColor Green
} catch {
    Write-Host "⚠ 未找到FFmpeg，视频处理功能将无法使用" -ForegroundColor Yellow
    Write-Host "  请参考README安装FFmpeg" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "启动 SmartCutElf..." -ForegroundColor Yellow
Write-Host ""

# 启动应用
python main.py

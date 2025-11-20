#!/bin/bash

echo "========================================"
echo "  SmartCutElf 快速打包脚本"
echo "========================================"
echo ""

echo "[1/3] 清理旧文件..."
rm -rf build dist
echo "  ✓ 清理完成"

echo ""
echo "[2/3] 开始打包..."
pyinstaller \
    --name=SmartCutElf \
    --windowed \
    --onefile \
    --clean \
    --noconfirm \
    --add-data="config.yaml:." \
    --add-data="assets:assets" \
    --hidden-import=PyQt5.QtMultimedia \
    --hidden-import=PyQt5.QtMultimediaWidgets \
    main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 打包失败！"
    exit 1
fi

echo "  ✓ 打包完成"

echo ""
echo "[3/3] 复制配置文件..."
cp config.yaml dist/
cp README.md dist/
cp -r assets dist/
echo "  ✓ 文件复制完成"

echo ""
echo "========================================"
echo "  ✨ 打包成功！"
echo "========================================"
echo ""
echo "📁 输出目录: dist/"
echo "📦 可执行文件: dist/SmartCutElf"
echo ""
echo "💡 提示: 可以直接运行 ./dist/SmartCutElf 测试"
echo ""

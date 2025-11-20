# SmartCutElf 智剪精灵

基于AI的智能视频自动剪辑软件。

## 📚 文档导航

所有文档已移动到 `docs/` 目录：

- [📖 使用说明](docs/使用说明.md) - 如何使用本软件
- [🚀 启动指南](docs/启动指南.md) - 安装和启动步骤
- [🔧 FFmpeg安装指南](docs/FFmpeg安装指南.md) - 视频处理环境配置
- [📝 项目文档](docs/README_PROJECT.md) - 项目详细说明
- [🏗️ 技术设计](docs/Technical_Design.md) - 详细技术架构设计

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

## 📦 核心功能

- **智能高光检测**：自动识别视频中的精彩片段
- **自动剪辑**：基于高光时刻自动裁剪和合并视频
- **字幕生成**：集成OpenAI Whisper自动生成字幕
- **画面调整**：支持横屏/竖屏自动转换
- **批量处理**：支持多线程批量处理视频文件

# SmartCutElf 智剪精灵

基于 AI 的智能视频自动剪辑软件

##  快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 FFmpeg（必须）
# 查看 docs/FFmpeg安装指南.md

# 3. 启动应用
python main.py
```

## ✨ 核心功能

- 🎯 **智能高光检测** - 自动识别精彩片段
- ✂️ **自动剪辑** - 3-5分钟精华内容
- 📝 **字幕生成** - OpenAI Whisper 自动字幕
- 🎨 **转场效果** - 10种转场类型
- ⚡ **批量处理** - 多线程并行
- ⚙️ **预设模式** - 6种处理模式快速切换
- 💾 **内存监控** - 实时监控系统资源
- ⏱️ **时间预估** - 智能预估处理时间
- 🔔 **桌面通知** - 处理完成自动提醒
- 📊 **友好提示** - 详细错误说明和解决方案

## � 文档

| 文档 | 说明 |
|------|------|
| [启动指南](docs/启动指南.md) | 安装和配置 |
| [使用说明](docs/使用说明.md) | 操作指南 |
| [FFmpeg安装](docs/FFmpeg安装指南.md) | FFmpeg 配置 |
| [部署指南](docs/部署指南.md) | 打包和分发 |
| [项目文档](docs/README_PROJECT.md) | 项目详情 |
| [技术设计](docs/Technical_Design.md) | 架构设计 |

## 🔨 打包部署

```bash
# Windows
quick_build.bat

# Linux/Mac
chmod +x quick_build.sh && ./quick_build.sh
```

**输出：**
- `dist/SmartCutElf.exe` - 可执行文件
- `SmartCutElf_v1.0.0_Portable.zip` - 便携版
- `installer_script.iss` - 安装脚本

## 🧪 测试

```bash
python run_tests.py
```

## 📝 更新日志

### v1.0.0 (2024-11-20)

**新增：**
- ✨ 10种转场效果
- ✨ 测试覆盖
- ✨ 打包配置

**优化：**
- 🎨 UI美化和缩放兼容
- 🔧 主题和配置管理

## ⚙️ 系统要求

- Python 3.8+
- FFmpeg（必须）
- 8GB+ 内存（推荐）

## � 许可证

MIT License

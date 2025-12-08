# SmartCutElf - 智剪精灵

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Personal%20Use-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)

**AI驱动的智能视频剪辑工具**

基于 Whisper 语音识别和智能分析，自动识别视频精彩片段并生成高质量剪辑

[功能特性](#核心功能) • [快速开始](#快速开始) • [使用文档](#文档) • [界面预览](#界面预览)

</div>

---

## ✨ 核心功能

- 🎬 **智能剪辑** - AI自动识别视频精彩片段，无需手动标记
- 🎙️ **语音识别** - 基于 OpenAI Whisper 模型的高精度语音转文字
- 📝 **字幕生成** - 自动生成时间轴精确的 SRT 字幕文件
- 🎨 **转场效果** - 支持淡入淡出等多种专业转场特效
- 🔊 **智能配音** - AI 语音合成，支持多种音色
- 🎵 **背景音乐** - 自动添加背景音乐并智能调节音量
- ⚙️ **灵活配置** - 支持自定义输出格式、分辨率、比特率等参数
- 🖥️ **现代UI** - 基于 PyQt5 的简洁易用图形界面，支持深色/浅色主题
- 📊 **实时监控** - 处理进度实时显示，日志详细记录
- 🚀 **高性能** - 支持多线程并行处理，充分利用系统资源

## �️ 速界面预览

<div align="center">
    <img src="https://m.360buyimg.com/i/jfs/t1/373843/2/6828/540799/693647e8F587204bc/6a2d71846166defe.png" alt="SmartCutElf 主界面" width="800"/>
    <p><i>主界面 - 简洁直观的操作面板</i></p>
    <br/>
    <img src="https://m.360buyimg.com/i/jfs/t1/372986/27/6362/259980/693647e7F4c4c0076/6361dbb48cfb0a55.png" alt="处理中" width="800"/>
    <p><i>处理状态 - 实时显示进度和日志</i></p>
    <br/>
    <img src="https://m.360buyimg.com/i/jfs/t1/373192/18/6652/582647/693647e9Fe0f207e1/ffebe27b5fab7d20.png" alt="设置界面" width="800"/>
    <p><i>设置选项 - 丰富的自定义配置</i></p>
</div>

## 🚀 快速开始

### 前置要求

- **Python**: 3.9 或更高版本
- **FFmpeg**: 必须安装并配置到系统 PATH
- **内存**: 建议 8GB 以上
- **系统**: Windows 10/11（主要支持）、macOS、Linux

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/SmartCutElf.git
cd SmartCutElf
```

2. **安装依赖**
```bash
pip install -r requirements.txt

# 如果下载速度慢，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **安装 FFmpeg**

详细安装步骤请参考 [FFmpeg安装指南](docs/FFmpeg安装指南.md)

验证安装：
```bash
ffmpeg -version
```

4. **运行程序**
```bash
python main.py

# 或使用快捷方式（Windows）
.\启动.bat
```

### 打包为可执行文件

```bash
# 使用构建脚本
python scripts/build.py

# 或使用快捷方式（Windows）
.\打包.bat

# 打包后的文件位于 dist/ 目录
```

## 📖 使用指南

### 基本流程

1. **打开视频文件夹** - 点击"打开文件夹"按钮选择包含视频的目录
2. **选择视频** - 在左侧列表中选择要处理的视频文件
3. **配置选项** - 根据需要启用字幕、配音、转场等功能
4. **开始处理** - 点击"开始处理"按钮，等待 AI 自动剪辑
5. **查看结果** - 处理完成后在 `output/` 目录查看生成的视频

### 配置说明

编辑 `config.yaml` 文件可自定义各项参数：

```yaml
processing:
  target_duration_min: 180    # 目标最小时长（秒）
  target_duration_max: 300    # 目标最大时长（秒）
  max_workers: 4              # 并行处理数量
  transition_enabled: true    # 启用转场效果
  transition_type: fade       # 转场类型

highlight:
  audio_weight: 0.4          # 音频高光权重
  video_weight: 0.4          # 视频高光权重
  sensitivity: medium        # 检测灵敏度

speech:
  recognition_model: base    # Whisper 模型（tiny/base/small/medium/large）
  tts_enabled: true          # 启用语音合成
  tts_voice: female          # 配音音色

output:
  format: mp4                # 输出格式
  resolution: 1080p          # 输出分辨率
  fps: 30                    # 帧率
  bitrate: 5000k            # 比特率
```

### 支持的格式

| 类型 | 格式 |
|------|------|
| **输入视频** | MP4, AVI, MOV, MKV, WMV, FLV |
| **输出视频** | MP4 (H.264 编码) |
| **字幕文件** | SRT |
| **音频编码** | AAC |

## 📚 文档

| 文档 | 说明 |
|------|------|
| [使用说明](docs/使用说明.md) | 详细的用户操作指南和使用技巧 |
| [启动指南](docs/启动指南.md) | 开发环境配置和依赖安装 |
| [部署指南](docs/部署指南.md) | 打包和发布说明 |
| [FFmpeg安装指南](docs/FFmpeg安装指南.md) | FFmpeg 详细配置教程 |
| [技术设计文档](docs/Technical_Design.md) | 系统架构和技术实现 |
| [开发笔记](docs/DEV_NOTES.md) | 开发过程中的技术要点和问题记录 |

## 📁 项目结构

```
SmartCutElf/
├── src/                      # 源代码目录
│   ├── ai/                  # AI 相关模块
│   │   ├── speech_recognition.py    # 语音识别（Whisper）
│   │   ├── subtitle_generator.py    # 字幕生成
│   │   └── text_to_speech.py        # 语音合成
│   ├── core/                # 核心处理模块
│   │   ├── audio_analyzer.py        # 音频分析
│   │   ├── video_analyzer.py        # 视频分析
│   │   ├── highlight_detector.py    # 高光检测
│   │   ├── video_processor.py       # 视频处理
│   │   ├── transition_effects.py    # 转场效果
│   │   └── workflow.py              # 工作流管理
│   ├── ui/                  # 用户界面
│   └── utils/               # 工具函数
├── assets/                   # 资源文件
│   ├── app_icon.ico         # 应用图标
│   └── screenshots/         # 界面截图
├── scripts/                  # 构建和工具脚本
│   ├── build.py             # 打包脚本
│   └── clear_cache.bat      # 清理缓存
├── docs/                     # 文档目录
├── logs/                     # 日志文件
├── data/                     # 数据目录
├── config.yaml              # 配置文件
├── requirements.txt         # Python 依赖
├── main.py                  # 程序入口
├── 启动.bat                 # Windows 启动脚本
└── 打包.bat                 # Windows 打包脚本
```

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| **Python** | 3.9+ 核心开发语言 |
| **PyQt5** | 图形界面框架 |
| **OpenAI Whisper** | 语音识别 AI 模型 |
| **FFmpeg** | 视频/音频处理引擎 |
| **OpenCV** | 计算机视觉和视频分析 |
| **NumPy** | 数值计算和数组处理 |
| **SciPy** | 科学计算和信号处理 |
| **PyYAML** | 配置文件管理 |
| **PyInstaller** | 打包为可执行文件 |

## 🔧 开发指南

### 开发环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
```

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型注解提高代码可读性
- 添加必要的注释和文档字符串
- 保持模块化和低耦合设计

### 调试技巧

- 查看日志文件：`logs/SmartCutElf_YYYYMMDD.log`
- 使用 `--debug` 参数启动获取详细日志
- 检查 `config.yaml` 配置是否正确

更多开发细节请参考 [开发笔记](docs/DEV_NOTES.md)

## ❓ 常见问题

### FFmpeg 未找到

**问题**：运行时提示找不到 FFmpeg

**解决**：
1. 确认 FFmpeg 已安装：`ffmpeg -version`
2. 将 FFmpeg 添加到系统 PATH
3. 或参考 [FFmpeg安装指南](docs/FFmpeg安装指南.md)

### Whisper 模型下载慢

**问题**：首次运行时模型下载速度慢

**解决**：
1. 使用更小的模型：在 `config.yaml` 中设置 `recognition_model: tiny`
2. 手动下载模型文件并放置到缓存目录
3. 使用代理或镜像加速

### 内存不足

**问题**：处理大视频时内存不足

**解决**：
1. 减少 `max_workers` 值（改为 2 或 1）
2. 使用更小的 Whisper 模型
3. 分段处理长视频
4. 增加系统虚拟内存

### 处理速度慢

**问题**：视频处理速度较慢

**解决**：
1. 使用 `tiny` 或 `base` 模型而非 `large`
2. 关闭不需要的功能（字幕、配音等）
3. 减少输出分辨率和比特率
4. 使用 GPU 加速（如果支持）

更多问题请查看 [使用说明](docs/使用说明.md) 或提交 Issue

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目仅供学习和个人使用。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [FFmpeg](https://ffmpeg.org/) - 优秀的多媒体处理工具
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台 GUI 框架

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by SmartCutElf Team

</div>

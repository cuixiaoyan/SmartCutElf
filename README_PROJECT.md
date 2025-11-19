# SmartCutElf - 智剪精灵

一款基于AI的智能视频自动剪辑软件，能够自动识别视频中的精彩片段，智能剪辑并生成字幕。

## 功能特点

✨ **智能高光检测** - 基于音频和视频分析，自动识别精彩片段
🎬 **自动视频剪辑** - 将长视频自动剪辑为3-5分钟精华内容
📝 **智能字幕生成** - 使用OpenAI Whisper进行语音识别，自动生成字幕
🎙️ **语音合成** - 支持文本转语音（TTS）
🎨 **现代化界面** - 深色主题，简洁易用
⚡ **高性能处理** - 多线程并行处理，支持批量操作

## 技术栈

- **界面框架**: PyQt5
- **视频处理**: FFmpeg + OpenCV
- **语音识别**: OpenAI Whisper
- **语音合成**: pyttsx3
- **数据库**: SQLite
- **配置管理**: YAML

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 安装FFmpeg

需要在系统中安装FFmpeg：

**Windows:**
1. 下载FFmpeg: https://ffmpeg.org/download.html
2. 解压并添加到系统PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

### 运行应用

```bash
python main.py
```

## 使用说明

1. **打开文件夹** - 点击"打开文件夹"按钮，选择包含视频文件的文件夹
2. **选择视频** - 从列表中查看扫描到的视频文件
3. **配置设置** - 根据需要调整剪辑参数（时长、字幕等）
4. **开始处理** - 点击"开始处理"按钮，等待自动剪辑完成
5. **查看结果** - 处理完成后，在输出文件夹中查看结果

## 项目结构

```
SmartCutElf/
├── main.py                 # 主程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖列表
├── src/
│   ├── ui/               # 用户界面
│   │   └── main_window.py
│   ├── core/             # 核心功能
│   │   ├── video_processor.py    # 视频处理
│   │   ├── audio_analyzer.py     # 音频分析
│   │   ├── video_analyzer.py     # 视频分析
│   │   └── highlight_detector.py # 高光检测
│   ├── ai/               # AI功能
│   │   ├── speech_recognition.py # 语音识别
│   │   ├── subtitle_generator.py # 字幕生成
│   │   └── text_to_speech.py     # 语音合成
│   └── utils/            # 工具模块
│       ├── config.py            # 配置管理
│       ├── logger.py            # 日志系统
│       ├── database.py          # 数据库管理
│       └── file_manager.py      # 文件管理
├── assets/               # 资源文件
├── logs/                 # 日志文件
├── cache/                # 缓存目录
└── output/               # 输出目录
```

## 配置说明

可以通过编辑`config.yaml`文件来自定义各项设置：

- **processing**: 处理参数（目标时长、工作线程数等）
- **highlight**: 高光检测参数（权重、灵敏度等）
- **subtitle**: 字幕样式设置
- **speech**: 语音识别和合成设置
- **ui**: 界面主题设置

## 系统要求

- Python 3.8+
- 8GB+ RAM
- FFmpeg
- （可选）CUDA支持的GPU用于加速

## 开发状态

当前版本: **v1.0.0**

- [x] 项目基础架构
- [x] 核心视频处理模块
- [x] AI功能集成
- [x] 用户界面
- [ ] 完整的处理流程集成
- [ ] 性能优化
- [ ] 测试和打包

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

项目主页: https://github.com/your-username/SmartCutElf

# SmartCutElf - 智剪精灵

基于 AI 的智能视频自动剪辑软件，自动识别精彩片段并生成字幕。

## ✨ 核心特性

| 功能 | 说明 |
|------|------|
| 🎯 智能高光检测 | 基于音频和视频分析，自动识别精彩片段 |
| ✂️ 自动剪辑 | 将长视频剪辑为 3-5 分钟精华内容 |
| 📝 字幕生成 | 使用 OpenAI Whisper 自动生成字幕 |
| 🎙️ 语音合成 | 支持文本转语音（TTS） |
| 🎨 转场效果 | 10 种转场效果（淡入淡出、滑动、缩放等） |
| 🖥️ 现代界面 | 深色/浅色主题，简洁易用 |
| ⚡ 批量处理 | 多线程并行处理 |

## 🛠️ 技术栈

```
界面：PyQt5
视频：FFmpeg + OpenCV
AI：OpenAI Whisper + pyttsx3
数据：SQLite + YAML
```

## 📁 项目结构

```
SmartCutElf/
├── main.py                    # 入口
├── config.yaml               # 配置
├── requirements.txt          # 依赖
├── src/
│   ├── ui/                   # 界面
│   │   ├── main_window.py
│   │   └── settings_dialog.py
│   ├── core/                 # 核心
│   │   ├── video_processor.py
│   │   ├── highlight_detector.py
│   │   ├── transition_effects.py
│   │   └── workflow.py
│   ├── ai/                   # AI
│   │   ├── speech_recognition.py
│   │   └── subtitle_generator.py
│   └── utils/                # 工具
│       ├── config.py
│       └── logger.py
├── tests/                    # 测试
├── docs/                     # 文档
└── output/                   # 输出
```

## 🎯 开发状态

**当前版本**: v1.0.0

| 模块 | 状态 |
|------|------|
| 基础架构 | ✅ 完成 |
| 视频处理 | ✅ 完成 |
| AI 功能 | ✅ 完成 |
| 用户界面 | ✅ 完成 |
| 转场效果 | ✅ 完成 |
| 测试覆盖 | ✅ 完成 |
| 打包部署 | ✅ 完成 |
| 性能优化 | 🔄 进行中 |

## 📚 文档

- [启动指南](启动指南.md) - 安装和配置
- [使用说明](使用说明.md) - 操作指南
- [FFmpeg安装](FFmpeg安装指南.md) - FFmpeg 配置
- [部署指南](部署指南.md) - 打包和分发
- [技术设计](Technical_Design.md) - 架构设计

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 FFmpeg（必须）
# 查看 docs/FFmpeg安装指南.md

# 3. 启动应用
python main.py
```

## ⚙️ 系统要求

- **Python**: 3.8+
- **内存**: 8GB+ 推荐
- **FFmpeg**: 必须安装
- **GPU**: 可选（CUDA 加速）

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

项目主页: https://github.com/your-username/SmartCutElf

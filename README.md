# SmartCutElf - 智剪精灵

**基于 AI 的智能视频剪辑工具**

自动识别视频高光片段，一键生成高质量短视频。
![undefined](https://img.meituan.net/portalweb/4e5b5cd71323cc565ebe5a49af698091690038.png)

---

## ✨ 核心功能

- **智能剪辑**：AI 自动识别精彩片段，无需手动标记
- **语音识别**：内置 Whisper 模型，精准语音转文字
- **自动字幕**：自动生成 SRT 字幕文件
- **智能配音**：支持 AI 语音合成与背景音乐混音
- **极简设计**：现代化 UI，操作更简单
- **高性能**：支持多线程并行处理，效率倍增

## 🚀 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置 FFmpeg**
   确保系统已安装 ffmpeg 并配置到环境变量。

3. **运行程序**
   ```bash
   python main.py
   ```

## 📖 使用说明

1. 点击 **"打开文件夹"** 选择视频目录。
2. 勾选 **"智能配音"** (可选)。
3. 点击 **"开始处理"**，坐等出片。
4. 结果将保存在 `output/` 文件夹中。

---

**Made with ❤️ by SmartCutElf Team**

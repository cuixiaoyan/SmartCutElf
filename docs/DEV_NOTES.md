# 开发笔记

## 最近修复 (2025-11-21)

### 打包问题修复
- ✅ 修复CMD终端窗口频繁弹出 - 为所有subprocess调用添加CREATE_NO_WINDOW标志
- ✅ 修复应用图标显示问题 - 使用PyInstaller资源路径处理
- ✅ 修复配置文件丢失 - 配置改为保存到用户AppData目录

### 配置管理
配置文件位置：`C:\Users\{用户名}\AppData\Roaming\SmartCutElf\config.yaml`

## 依赖管理

### 核心依赖
```
PyQt5>=5.15.0
numpy>=1.24.0
opencv-python>=4.8.0
ffmpeg-python>=0.2.0
openai-whisper>=20231117
PyYAML>=6.0
```

### 已排除的依赖（打包优化）
- torch (1GB+) - 打包时排除，运行时由Whisper自动下载
- scipy - 非必需，已移除
- pyttsx3 - TTS功能暂未使用

## 打包说明

### 快速打包 (约40秒)
```bash
python scripts/build.py
```

### 优化策略
- 使用onedir模式（比onefile快20倍）
- 排除torch和不需要的PyQt5模块
- 输出大小约420MB

## FFmpeg配置

需要在系统PATH中或项目指定路径配置FFmpeg。详见 [FFmpeg安装指南](FFmpeg安装指南.md)

## 已知问题

### Windows控制台窗口
- **已修复** - 所有subprocess调用已添加CREATE_NO_WINDOW标志

### Unicode路径问题
- FFmpeg在Windows上处理中文路径时使用临时目录避免编码问题

## 项目结构

```
src/
├── core/
│   ├── video_processor.py    # 视频处理（FFmpeg封装）
│   └── ai_processor.py        # AI处理（Whisper集成）
├── ui/
│   ├── main_window.py         # 主窗口
│   └── settings_dialog.py     # 设置对话框
└── utils/
    ├── config.py              # 配置管理
    ├── logger.py              # 日志系统
    └── notifications.py       # 系统通知
```

## 开发技巧

### 日志调试
日志文件位置：`logs/smartcutelf.log`

### 配置重置
删除配置文件即可重置：
```powershell
Remove-Item "$env:APPDATA\SmartCutElf\config.yaml"
```

### 增量打包
去掉build.py中的`--clean`参数可加快重复打包速度

## 性能优化

- 使用多线程处理视频片段
- FFmpeg参数优化（preset=fast, crf=23）
- 临时文件及时清理

## 待办事项

- [ ] 增加批量处理功能
- [ ] 优化AI模型加载速度
- [ ] 支持更多视频格式
- [ ] 添加视频预览功能

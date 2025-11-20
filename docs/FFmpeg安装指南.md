# FFmpeg 快速安装指南（Windows）

## 方法1：使用Scoop（推荐，最简单）

1. 安装Scoop（如果还没有）：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

2. 安装FFmpeg：
```powershell
scoop install ffmpeg
```

3. 验证安装：
```powershell
ffmpeg -version
```

## 方法2：手动安装

1. **下载FFmpeg**：
   - 访问：https://github.com/BtbN/FFmpeg-Builds/releases
   - 下载：`ffmpeg-master-latest-win64-gpl.zip`

2. **解压文件**：
   - 解压到：`C:\ffmpeg`（推荐路径）
   - 确保bin目录在：`C:\ffmpeg\bin`

3. **添加到PATH环境变量**：
   - 按 `Win + X`，选择"系统"
   - 点击"高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到"Path"
   - 点击"编辑" → "新建"
   - 添加：`C:\ffmpeg\bin`
   - 点击"确定"保存所有对话框

4. **验证安装**：
   - 打开新的PowerShell窗口
   - 运行：`ffmpeg -version`
   - 如果显示版本信息，说明安装成功

## 方法3：使用Chocolatey

```powershell
choco install ffmpeg
```

## 验证FFmpeg是否正确安装

运行以下命令，应该看到版本信息：
```powershell
ffmpeg -version
ffprobe -version
```

## 安装完成后

重新启动SmartCutElf：
```bash
python main.py
```

现在视频处理功能应该可以正常工作了！

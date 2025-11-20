# SmartCutElf 文档目录

## 核心文档

### [依赖优化说明](依赖优化说明.md)
- 核心依赖列表
- 已排除的依赖
- scipy和pyttsx3问题修复
- 依赖安装和验证

### [打包优化说明](打包优化说明.md)
- 极速打包方法（40秒）
- 优化效果对比
- onedir vs onefile
- 注意事项

### [问题修复记录](问题修复记录.md)
- PyQt5 DLL加载失败
- scipy模块缺失
- numpy.testing运行时错误
- Python版本兼容性

### [项目结构说明](项目结构说明.md)
- 完整目录结构
- 文件说明
- 开发工作流
- 文件命名规范

## 其他文档

- [FFmpeg安装指南](FFmpeg安装指南.md) - FFmpeg配置
- [Technical_Design](Technical_Design.md) - 技术架构设计

## 快速链接

### 安装依赖
```bash
pip install -r requirements.txt
```

### 打包程序
```bash
python scripts\build.py
```

### 运行程序
```bash
python main.py
```

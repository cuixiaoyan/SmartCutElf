"""
SmartCutElf 打包脚本
使用 PyInstaller 打包应用程序（优化版，约40秒）
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✓ 已删除 {dir_name}/")


def build_executable():
    """打包可执行文件"""
    print("\n🚀 开始打包...")
    print("  💡 优化策略：")
    print("     1. 使用onedir模式（比onefile快20倍+）")
    print("     2. 排除torch（减少1GB，Whisper会自动下载）")
    print("     3. 排除不需要的PyQt5模块")
    print("     4. 排除测试模块\n")
    
    # PyInstaller 参数（优化版）
    cmd = [
        'pyinstaller',
        '--name=SmartCutElf',
        '--windowed',
        
        # ⚡⚡⚡ 关键：onedir模式（不要用onefile）
        # onedir: 1-3分钟
        # onefile: 10-30分钟
        
        '--noconfirm',
        '--clean',
        
        # ⚡ 添加src到路径
        '--paths=src',
        
        # 数据文件
        '--add-data=config.yaml;.',
        '--add-data=assets;assets',
        
        # ⚡ 隐式导入（只导入必需的）
        '--hidden-import=PyQt5.QtMultimedia',
        '--hidden-import=PyQt5.QtMultimediaWidgets',
        
        # ⚡⚡⚡ 排除超大型模块（最关键的优化）
        '--exclude-module=torch',           # 1GB+ (Whisper会自动下载)
        '--exclude-module=torch.distributions',
        '--exclude-module=torch.testing',
        '--exclude-module=torch.autograd',
        '--exclude-module=torch.cuda',
        '--exclude-module=torchvision',
        '--exclude-module=torchaudio',
        
        # ⚡ 排除开发工具
        '--exclude-module=pytest',
        '--exclude-module=setuptools',
        '--exclude-module=pip',
        '--exclude-module=wheel',
        
        # ⚡ 排除不需要的GUI库
        '--exclude-module=tkinter',
        '--exclude-module=PyQt5.QtWebEngine',
        '--exclude-module=PyQt5.QtWebEngineWidgets',
        '--exclude-module=PyQt5.QtNetwork',
        '--exclude-module=PyQt5.QtSql',
        '--exclude-module=PyQt5.QtTest',
        '--exclude-module=PyQt5.QtXml',
        '--exclude-module=PyQt5.QtBluetooth',
        '--exclude-module=PyQt5.QtDBus',
        '--exclude-module=PyQt5.QtDesigner',
        '--exclude-module=PyQt5.QtHelp',
        '--exclude-module=PyQt5.QtLocation',
        '--exclude-module=PyQt5.QtNfc',
        '--exclude-module=PyQt5.QtPositioning',
        '--exclude-module=PyQt5.QtQml',
        '--exclude-module=PyQt5.QtQuick',
        '--exclude-module=PyQt5.QtQuickWidgets',
        '--exclude-module=PyQt5.QtSensors',
        '--exclude-module=PyQt5.QtSerialPort',
        '--exclude-module=PyQt5.QtWebChannel',
        '--exclude-module=PyQt5.QtWebSockets',
        '--exclude-module=PyQt5.QtXmlPatterns',
        
        # ⚡ 排除数据科学库
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--exclude-module=PIL.ImageTk',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        '--exclude-module=notebook',
        
        # ⚡ 排除测试模块（注意：不要排除numpy.testing，某些模块会导入它）
        # '--exclude-module=numpy.testing',  # ❌ 不要排除，会导致运行时错误
        '--exclude-module=scipy.testing',
        '--exclude-module=cv2.typing',
        
        # 图标
        '--icon=assets/app_icon.ico',
        
        # 主程序
        'main.py'
    ]
    
    # Windows/Linux 路径分隔符
    if sys.platform != 'win32':
        cmd = [arg.replace(';', ':') for arg in cmd]
    
    try:
        start_time = time.time()
        
        print(f"  ⏳ 打包中...\n")
        result = subprocess.run(cmd, check=True)
        
        elapsed = time.time() - start_time
        print(f"\n  ✓ 打包成功！")
        print(f"  ⏱️  耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
        
        # 显示输出大小
        dist_path = Path('dist/SmartCutElf')
        if dist_path.exists():
            size_mb = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file()) / (1024*1024)
            print(f"  📦 输出大小: {size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ 打包失败，退出代码: {e.returncode}")
        return False
    except FileNotFoundError:
        print("  ❌ 找不到 pyinstaller 命令")
        return False


def show_tips():
    """显示优化提示"""
    print("\n" + "="*70)
    print("📌 打包速度优化提示")
    print("="*70)
    print("""
1. ⚡ 使用onedir模式（当前配置）
   - onedir: 1-3分钟
   - onefile: 10-30分钟
   - 建议：开发阶段用onedir，发布时再考虑onefile

2. ⚡ 排除torch和Whisper模型（当前配置）
   - torch约1GB，Whisper模型75MB-3GB
   - 首次运行时会自动下载Whisper模型
   - 减少打包体积和时间

3. ⚡ 使用--noupx（如果安装了UPX）
   - UPX压缩会大幅增加打包时间
   - 如果不需要极致压缩，可以禁用

4. ⚡ 增量打包
   - 不要每次都用--clean
   - 只在依赖变化时清理

5. ⚡ 使用SSD硬盘
   - 打包涉及大量文件读写
   - SSD可以提速50%+

6. ⚡ 关闭杀毒软件实时扫描
   - 杀毒软件会扫描每个生成的文件
   - 临时添加dist/build目录到白名单

7. ⚡ 使用虚拟环境
   - 只安装必需的包
   - 避免扫描不相关的包
""")
    print("="*70)




def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          SmartCutElf 打包脚本                                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"\n✓ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("\n❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return
    
    # 清理旧文件
    clean_build_dirs()
    
    # 打包
    success = build_executable()
    
    if success:
        print("\n" + "="*70)
        print("🎉 打包成功！")
        print("="*70)
        print(f"\n📂 输出位置: {os.path.abspath('dist/SmartCutElf')}")
        print(f"🚀 运行程序: dist\\SmartCutElf\\SmartCutElf.exe")
        
        # 显示优化提示
        show_tips()
    else:
        print("\n❌ 打包失败，请检查错误信息")


if __name__ == '__main__':
    main()

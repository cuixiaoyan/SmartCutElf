"""
SmartCutElf 打包脚本
使用 PyInstaller 打包应用程序
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✓ 已删除 {dir_name}/")


def check_dependencies():
    """检查依赖"""
    print("\n📦 检查依赖...")
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("  ❌ PyInstaller 未安装")
        print("  请运行: pip install pyinstaller")
        return False
    
    return True


def build_executable():
    """构建可执行文件"""
    print("\n🔨 开始打包...")
    
    # PyInstaller 参数
    cmd = [
        'pyinstaller',
        '--name=SmartCutElf',
        '--windowed',  # 不显示控制台窗口
        '--onefile',   # 打包成单个文件
        '--clean',     # 清理临时文件
        '--noconfirm', # 不确认覆盖
        
        # 添加数据文件
        '--add-data=config.yaml;.',
        '--add-data=assets;assets',
        
        # 添加隐藏导入
        '--hidden-import=PyQt5.QtMultimedia',
        '--hidden-import=PyQt5.QtMultimediaWidgets',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=whisper',
        '--hidden-import=pyttsx3',
        
        # 图标（如果存在）
        '--icon=assets/app_icon.ico',
        
        # 主程序入口
        'main.py'
    ]
    
    # 在 Windows 上需要使用分号，在 Linux/Mac 上使用冒号
    if sys.platform != 'win32':
        cmd = [arg.replace(';', ':') for arg in cmd]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ 打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 打包失败: {e}")
        print(f"  错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  ❌ 找不到 pyinstaller 命令")
        print("  请确保 PyInstaller 已正确安装")
        return False


def create_installer_script():
    """创建安装程序脚本（Inno Setup）"""
    print("\n📝 创建安装程序脚本...")
    
    inno_script = """
; SmartCutElf 安装程序脚本
; 使用 Inno Setup 编译

[Setup]
AppName=SmartCutElf 智剪精灵
AppVersion=1.0.0
AppPublisher=SmartCutElf Team
DefaultDirName={autopf}\\SmartCutElf
DefaultGroupName=SmartCutElf
OutputDir=installer
OutputBaseFilename=SmartCutElf_Setup_v1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"

[Files]
Source: "dist\\SmartCutElf.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.yaml"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\\*"; DestDir: "{app}\\assets"; Flags: ignoreversion recursesubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\SmartCutElf 智剪精灵"; Filename: "{app}\\SmartCutElf.exe"
Name: "{group}\\卸载 SmartCutElf"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\SmartCutElf 智剪精灵"; Filename: "{app}\\SmartCutElf.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\SmartCutElf.exe"; Description: "启动 SmartCutElf"; Flags: nowait postinstall skipifsilent
"""
    
    script_path = Path('installer_script.iss')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(inno_script)
    
    print(f"  ✓ 已创建 {script_path}")
    print("  💡 使用 Inno Setup 编译此脚本以创建安装程序")


def copy_dependencies():
    """复制依赖文件到 dist 目录"""
    print("\n📋 复制依赖文件...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ⚠️ dist 目录不存在，跳过")
        return
    
    # 复制配置文件
    files_to_copy = [
        'config.yaml',
        'README.md',
    ]
    
    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = dist_dir / file_name
            shutil.copy2(src, dst)
            print(f"  ✓ 已复制 {file_name}")
    
    # 复制 assets 目录
    assets_src = Path('assets')
    if assets_src.exists():
        assets_dst = dist_dir / 'assets'
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)
        print(f"  ✓ 已复制 assets/")


def create_portable_package():
    """创建便携版压缩包"""
    print("\n📦 创建便携版...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ⚠️ dist 目录不存在，跳过")
        return
    
    # 创建便携版目录
    portable_dir = Path('SmartCutElf_Portable')
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制文件
    exe_file = dist_dir / 'SmartCutElf.exe'
    if exe_file.exists():
        shutil.copy2(exe_file, portable_dir)
        print(f"  ✓ 已复制可执行文件")
    
    # 复制其他文件
    for item in ['config.yaml', 'README.md', 'assets']:
        src = dist_dir / item
        if src.exists():
            if src.is_file():
                shutil.copy2(src, portable_dir / item)
            else:
                shutil.copytree(src, portable_dir / item)
            print(f"  ✓ 已复制 {item}")
    
    # 创建必要的目录
    for dir_name in ['output', 'logs', 'cache']:
        (portable_dir / dir_name).mkdir(exist_ok=True)
    
    # 压缩为 zip
    try:
        import zipfile
        zip_name = 'SmartCutElf_v1.0.0_Portable.zip'
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(portable_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(portable_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"  ✓ 已创建 {zip_name}")
        
        # 清理临时目录
        shutil.rmtree(portable_dir)
        
    except Exception as e:
        print(f"  ❌ 创建压缩包失败: {e}")


def print_summary():
    """打印总结信息"""
    print("\n" + "="*60)
    print("✨ 打包完成！")
    print("="*60)
    print("\n📁 输出文件：")
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        exe_file = dist_dir / 'SmartCutElf.exe'
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"  • 可执行文件: dist/SmartCutElf.exe ({size_mb:.1f} MB)")
    
    portable_zip = Path('SmartCutElf_v1.0.0_Portable.zip')
    if portable_zip.exists():
        size_mb = portable_zip.stat().st_size / (1024 * 1024)
        print(f"  • 便携版: {portable_zip.name} ({size_mb:.1f} MB)")
    
    installer_script = Path('installer_script.iss')
    if installer_script.exists():
        print(f"  • 安装脚本: {installer_script.name}")
    
    print("\n📝 后续步骤：")
    print("  1. 测试 dist/SmartCutElf.exe 是否正常运行")
    print("  2. 使用 Inno Setup 编译 installer_script.iss 创建安装程序")
    print("  3. 分发便携版 ZIP 文件或安装程序")
    print("\n💡 提示：")
    print("  • 首次运行可能需要安装 FFmpeg")
    print("  • 确保目标系统已安装 Visual C++ Redistributable")
    print()


def main():
    """主函数"""
    print("="*60)
    print("  SmartCutElf 打包工具")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 清理旧文件
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        print("\n❌ 打包失败")
        return 1
    
    # 复制依赖文件
    copy_dependencies()
    
    # 创建便携版
    create_portable_package()
    
    # 创建安装程序脚本
    create_installer_script()
    
    # 打印总结
    print_summary()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

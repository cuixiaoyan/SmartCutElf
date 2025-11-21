"""
SmartCutElf - 智剪精灵
视频自动剪辑软件

主程序入口
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from utils.logger import setup_logger
from utils.config import Config


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持PyInstaller打包）"""
    # PyInstaller会将临时文件夹路径存储到_MEIPASS
    base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)
    return str(Path(base_path) / relative_path)


def main():
    """主函数"""
    # 初始化日志系统
    logger = setup_logger()
    logger.info("="*60)
    logger.info("SmartCutElf 智剪精灵 启动中...")
    logger.info("="*60)
    
    # 加载配置
    config = Config()
    config.load()
    
    # 设置 AppUserModelID (修复任务栏图标显示问题)
    try:
        # 格式: company.product.subproduct.version
        myappid = 'smartcutelf.app.gui.1.0.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        logger.error(f"设置 AppUserModelID 失败: {e}")
    
    # 高DPI支持 (必须在创建QApplication之前设置)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("SmartCutElf")
    app.setOrganizationName("SmartCutElf")
    
    # 设置应用图标（全局生效：任务栏、窗口等）
    icon_path = get_resource_path('assets/app_icon.ico')
    if Path(icon_path).exists():
        app.setWindowIcon(QIcon(icon_path))
        logger.info(f"应用图标已设置: {icon_path}")
    else:
        logger.warning(f"图标文件未找到: {icon_path}")
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    logger.info("应用程序界面已启动")
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

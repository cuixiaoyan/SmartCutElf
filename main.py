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

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from utils.logger import setup_logger
from utils.config import Config


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
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("SmartCutElf")
    app.setOrganizationName("SmartCutElf")
    
    # 高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    logger.info("应用程序界面已启动")
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

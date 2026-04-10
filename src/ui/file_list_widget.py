"""
文件列表组件 - 增强版
支持图标、状态指示、右键菜单
"""

from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QMenu, QAction,
                             QHBoxLayout, QLabel, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap
from pathlib import Path


class FileListWidgetItem(QListWidgetItem):
    """增强的文件列表项"""

    # 状态枚举
    STATUS_PENDING = 0
    STATUS_PROCESSING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3

    def __init__(self, file_data: dict):
        super().__init__()
        self.file_data = file_data
        self.status = self.STATUS_PENDING

    def set_status(self, status: int):
        """设置状态"""
        self.status = status
        self.update_display()

    def update_display(self):
        """更新显示"""
        status_icons = {
            self.STATUS_PENDING: '⏳',
            self.STATUS_PROCESSING: '⚙️',
            self.STATUS_SUCCESS: '✅',
            self.STATUS_FAILED: '❌'
        }

        icon = status_icons.get(self.status, '⏳')
        name = self.file_data['name']
        size_mb = self.file_data['size_mb']

        self.setText(f"{icon} {name}\n    {size_mb:.1f} MB")


class EnhancedFileListWidget(QListWidget):
    """增强的文件列表组件"""

    # 信号定义
    file_selected = pyqtSignal(dict)  # 文件被选中
    files_removed = pyqtSignal(list)  # 文件被移除

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_context_menu()
        self.files_data = []

    def _setup_ui(self):
        """设置UI"""
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragDropMode(QListWidget.DropOnly)

        # 不设置样式，使用全局主题样式

    def _setup_context_menu(self):
        """设置右键菜单"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        # 从列表中移除
        remove_action = QAction('🗑️ 从列表中移除', self)
        remove_action.triggered.connect(lambda: self._remove_item(item))
        menu.addAction(remove_action)

        # 打开文件位置
        location_action = QAction('📁 打开文件位置', self)
        location_action.triggered.connect(lambda: self._open_file_location(item))
        menu.addAction(location_action)

        # 查看详情
        detail_action = QAction('📊 查看详情', self)
        detail_action.triggered.connect(lambda: self._show_file_detail(item))
        menu.addAction(detail_action)

        menu.exec_(self.mapToGlobal(pos))

    def _remove_item(self, item):
        """移除项目"""
        row = self.row(item)
        self.takeItem(row)

        # 更新文件数据列表
        if hasattr(item, 'file_data'):
            self.files_data.remove(item.file_data)

        # 发送信号
        self.files_removed.emit([item.file_data] if hasattr(item, 'file_data') else [])

    def _open_file_location(self, item):
        """打开文件位置"""
        if not hasattr(item, 'file_data'):
            return

        file_path = item.file_data.get('path')
        if file_path and Path(file_path).exists():
            import subprocess
            import sys

            file_path = Path(file_path).parent

            if sys.platform == 'win32':
                subprocess.run(['explorer', str(file_path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(file_path)])
            else:
                subprocess.run(['xdg-open', str(file_path)])

    def _show_file_detail(self, item):
        """显示文件详情"""
        if not hasattr(item, 'file_data'):
            return

        file_data = item.file_data
        detail_text = f"""📹 文件名: {file_data['name']}
📏 大小: {file_data['size_mb']:.2f} MB
🎞️ 格式: {file_data['extension']}
📁 路径: {file_data['path']}
📅 修改时间: {file_data['modified'].strftime('%Y-%m-%d %H:%M:%S')}
"""

        self.file_selected.emit(file_data)

    def add_video_file(self, file_data: dict):
        """添加视频文件"""
        self.files_data.append(file_data)

        item = FileListWidgetItem(file_data)
        self.addItem(item)

        return item

    def update_file_status(self, file_path: str, status: int):
        """更新文件状态"""
        for i in range(self.count()):
            item = self.item(i)
            if hasattr(item, 'file_data') and item.file_data['path'] == file_path:
                item.set_status(status)
                break

    def clear_files(self):
        """清空文件列表"""
        self.clear()
        self.files_data = []

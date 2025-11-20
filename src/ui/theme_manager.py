"""
主题管理器
支持深色/浅色主题切换，Apple风格设计
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict


class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题切换信号
    
    def __init__(self):
        super().__init__()
        self.current_theme = 'light'
        self.themes = {
            'light': self._get_light_theme(),
            'dark': self._get_dark_theme()
        }
    
    def _get_light_theme(self) -> Dict[str, str]:
        """浅色主题配置"""
        return {
            # 主色调
            'primary': '#007AFF',           # 苹果蓝
            'primary_hover': '#0051D5',
            'primary_pressed': '#004FC4',
            
            # 背景色
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F5F7',
            'bg_tertiary': '#E8E8ED',
            'bg_elevated': '#FFFFFF',
            
            # 文字颜色
            'text_primary': '#1D1D1F',
            'text_secondary': '#6E6E73',
            'text_tertiary': '#86868B',
            'text_link': '#007AFF',
            
            # 边框和分隔线
            'border': '#D2D2D7',
            'separator': '#E5E5EA',
            
            # 状态色
            'success': '#34C759',
            'warning': '#FF9500',
            'error': '#FF3B30',
            'info': '#5AC8FA',
            
            # 阴影
            'shadow': 'rgba(0, 0, 0, 0.1)',
            'shadow_strong': 'rgba(0, 0, 0, 0.15)',
            
            # 特殊效果
            'overlay': 'rgba(0, 0, 0, 0.3)',
            'glass_bg': 'rgba(255, 255, 255, 0.7)',
        }
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """深色主题配置"""
        return {
            # 主色调
            'primary': '#0A84FF',
            'primary_hover': '#409CFF',
            'primary_pressed': '#0077ED',
            
            # 背景色
            'bg_primary': '#1C1C1E',
            'bg_secondary': '#2C2C2E',
            'bg_tertiary': '#3A3A3C',
            'bg_elevated': '#2C2C2E',
            
            # 文字颜色
            'text_primary': '#FFFFFF',
            'text_secondary': '#EBEBF5',
            'text_tertiary': '#AEAEB2',
            'text_link': '#0A84FF',
            
            # 边框和分隔线
            'border': '#38383A',
            'separator': '#48484A',
            
            # 状态色
            'success': '#32D74B',
            'warning': '#FF9F0A',
            'error': '#FF453A',
            'info': '#64D2FF',
            
            # 阴影
            'shadow': 'rgba(0, 0, 0, 0.3)',
            'shadow_strong': 'rgba(0, 0, 0, 0.5)',
            
            # 特殊效果
            'overlay': 'rgba(0, 0, 0, 0.5)',
            'glass_bg': 'rgba(28, 28, 30, 0.7)',
        }
    
    def get_stylesheet(self) -> str:
        """获取当前主题的完整样式表"""
        colors = self.themes[self.current_theme]
        
        return f"""
            /* ========== 全局样式 ========== */
            QMainWindow {{
                background-color: {colors['bg_primary']};
            }}
            
            QWidget {{
                color: {colors['text_primary']};
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
            }}
            
            /* ========== 按钮样式 ========== */
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-height: 36px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary_pressed']};
                padding: 9px 20px 7px 20px;
            }}
            
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_tertiary']};
            }}
            
            /* 次要按钮 */
            QPushButton[secondary="true"] {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
            }}
            
            QPushButton[secondary="true"]:hover {{
                background-color: {colors['bg_tertiary']};
            }}
            
            /* ========== 工具栏 ========== */
            QToolBar {{
                background-color: {colors['bg_elevated']};
                border: none;
                border-bottom: 1px solid {colors['separator']};
                spacing: 8px;
                padding: 8px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                color: {colors['text_primary']};
            }}
            
            QToolButton:hover {{
                background-color: {colors['bg_secondary']};
            }}
            
            QToolButton:pressed {{
                background-color: {colors['bg_tertiary']};
            }}
            
            /* ========== 列表样式 ========== */
            QListWidget {{
                background-color: {colors['bg_primary']};
                border: none;
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 12px;
                margin: 4px 6px;
                color: {colors['text_primary']};
                font-size: 13px;
                line-height: 1.5;
            }}
            
            QListWidget::item:hover {{
                background-color: {colors['bg_secondary']};
                border-color: {colors['primary']};
            }}
            
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
                color: white;
            }}
            
            /* ========== 文本编辑框 ========== */
            QTextEdit, QLineEdit {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px;
                color: {colors['text_primary']};
                font-size: 13px;
                selection-background-color: {colors['primary']};
            }}
            
            QTextEdit:focus, QLineEdit:focus {{
                border: 2px solid {colors['primary']};
                padding: 9px;
            }}
            
            /* ========== 进度条 ========== */
            QProgressBar {{
                background-color: {colors['bg_secondary']};
                border: none;
                border-radius: 6px;
                min-height: 24px;
                max-height: 24px;
                text-align: center;
                font-size: 12px;
                font-weight: 600;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors['primary']};
                border-radius: 6px;
            }}
            
            /* ========== 分组框 ========== */
            QGroupBox {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 10px;
                margin-top: 16px;
                padding: 18px 14px 14px 14px;
                font-weight: 600;
                font-size: 14px;
                color: {colors['text_primary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background-color: {colors['bg_elevated']};
                color: {colors['text_primary']};
                font-weight: 700;
            }}
            
            /* ========== 复选框 ========== */
            QCheckBox {{
                spacing: 8px;
                color: {colors['text_primary']};
                font-size: 13px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {colors['border']};
                background-color: {colors['bg_elevated']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTUgMTJMMTAgMTdMMTkgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {colors['primary']};
            }}
            
            /* ========== 单选按钮 ========== */
            QRadioButton {{
                spacing: 8px;
                color: {colors['text_primary']};
                font-size: 13px;
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {colors['border']};
                background-color: {colors['bg_elevated']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iNiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }}
            
            QRadioButton::indicator:hover {{
                border-color: {colors['primary']};
            }}
            
            /* ========== 滚动条 ========== */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['text_tertiary']};
                border-radius: 4px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['text_secondary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors['text_tertiary']};
                border-radius: 4px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['text_secondary']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ========== 菜单栏 ========== */
            QMenuBar {{
                background-color: {colors['bg_elevated']};
                border-bottom: 1px solid {colors['separator']};
                padding: 4px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 6px;
                color: {colors['text_primary']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors['bg_secondary']};
            }}
            
            QMenu {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
                color: {colors['text_primary']};
            }}
            
            QMenu::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            /* ========== 状态栏 ========== */
            QStatusBar {{
                background-color: {colors['bg_elevated']};
                border-top: 1px solid {colors['separator']};
                color: {colors['text_secondary']};
                font-size: 12px;
                padding: 6px 10px;
            }}
            
            /* ========== 分隔器 ========== */
            QSplitter::handle {{
                background-color: {colors['separator']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            
            QSplitter::handle:vertical {{
                height: 1px;
            }}
            
            /* ========== 标签页 ========== */
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 10px;
                background-color: {colors['bg_elevated']};
            }}
            
            QTabBar::tab {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_secondary']};
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['bg_elevated']};
                color: {colors['text_primary']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {colors['bg_tertiary']};
            }}
            
            /* ========== 下拉框 ========== */
            QComboBox {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 6px 8px;
                color: {colors['text_primary']};
                font-size: 13px;
                min-height: 28px;
            }}
            
            QComboBox:hover {{
                border-color: {colors['primary']};
            }}
            
            QComboBox:focus {{
                border: 2px solid {colors['primary']};
                padding: 5px 7px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                selection-background-color: {colors['primary']};
                outline: none;
                padding: 4px;
            }}
            
            /* ========== 数字输入框 ========== */
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 6px 8px;
                color: {colors['text_primary']};
                font-size: 13px;
                min-height: 28px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {colors['primary']};
                padding: 5px 7px;
            }}
            
            /* ========== 标签 ========== */
            QLabel {{
                font-size: 13px;
                color: {colors['text_primary']};
            }}
            
            /* ========== 对话框 ========== */
            QDialog {{
                background-color: {colors['bg_primary']};
            }}
            
            QMessageBox {{
                background-color: {colors['bg_primary']};
            }}
        """
    
    def set_theme(self, theme_name: str):
        """切换主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
    
    def toggle_theme(self):
        """切换深色/浅色主题"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme)
    
    def apply_theme(self, app: QApplication):
        """应用主题到应用程序"""
        app.setStyleSheet(self.get_stylesheet())
    
    def get_color(self, color_key: str) -> str:
        """获取当前主题的颜色值"""
        return self.themes[self.current_theme].get(color_key, '#000000')


# 全局主题管理器实例
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器实例"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

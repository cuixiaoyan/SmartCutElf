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
        self.current_theme = 'light' # 强制默认为浅色
        self.themes = {
            'light': self._get_light_theme(),
            'dark': self._get_light_theme() # 即使请求dark也返回light
        }
    
    def _get_light_theme(self) -> Dict[str, str]:
        """浅色主题配置 (iOS风格 - 淡紫色)"""
        return {
            # 主色调 - 淡紫色
            'primary': '#9F85FF',           # 软紫色
            'primary_hover': '#8A6EFF',
            'primary_pressed': '#7B5DFF',
            
            # 背景色
            'bg_primary': '#F2F2F7',        # iOS设置页背景灰
            'bg_secondary': '#FFFFFF',      # 卡片白
            'bg_tertiary': '#F5F5FA',       # 略深一点
            'bg_elevated': '#FFFFFF',       # 浮层白
            
            # 文字颜色
            'text_primary': '#000000',
            'text_secondary': '#3C3C43',    # iOS Secondary Label (60% opacity look)
            'text_tertiary': '#D1D1D6',
            'text_link': '#9F85FF',
            
            # 边框和分隔线
            'border': '#E5E5EA',
            'separator': '#C6C6C8',
            
            # 状态色
            'success': '#34C759',
            'warning': '#FF9500',
            'error': '#FF3B30',
            'info': '#5AC8FA',
            
            # 阴影
            'shadow': 'rgba(0, 0, 0, 0.05)',
            'shadow_strong': 'rgba(0, 0, 0, 0.1)',
            
            # 特殊效果
            'overlay': 'rgba(0, 0, 0, 0.2)',
            'glass_bg': 'rgba(255, 255, 255, 0.8)',
        }
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """深色主题配置 (兼容iOS风格)"""
        return {
            # 主色调 - 深色模式下稍微提亮一点
            'primary': '#0A84FF',           # iOS Blue
            'primary_hover': '#409CFF',
            'primary_pressed': '#0071E3',
            
            # 背景色 - 使用深灰层次
            'bg_primary': '#000000',        # 纯黑背景
            'bg_secondary': '#1C1C1E',      # 卡片深灰
            'bg_tertiary': '#2C2C2E',       # 如果有第三层
            'bg_elevated': '#3A3A3C',       # 浮层/输入框
            
            # 文字颜色
            'text_primary': '#FFFFFF',
            'text_secondary': '#EBEBF5',    # 60% white
            'text_tertiary': '#AEAEB2',     # 30% white
            'text_link': '#0A84FF',
            
            # 边框和分隔线
            'border': '#38383A',
            'separator': '#48484A',
            
            # 状态色
            'success': '#30D158',
            'warning': '#FF9F0A',
            'error': '#FF453A',
            'info': '#64D2FF',
            
            # 阴影 (深色模式下主要是光晕或更深的阴影)
            'shadow': 'rgba(0, 0, 0, 0.5)',
            'shadow_strong': 'rgba(0, 0, 0, 0.8)',
            
            # 特殊效果
            'overlay': 'rgba(0, 0, 0, 0.6)',
            'glass_bg': 'rgba(30, 30, 30, 0.8)',
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
                font-family: -apple-system, "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
                font-size: 13px; /* 全局字体稍微调小一点 */
            }}
            
            /* ========== 按钮样式 ========== */
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px; /* 圆角稍微收一点 */
                padding: 5px 12px; /* 减小内边距 */
                font-weight: 600;
                font-size: 13px;
                min-height: 24px; /* 减小最小高度 */
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary_pressed']};
                padding: 6px 12px 4px 12px;
            }}
            
            QPushButton:checked {{
                background-color: {colors['primary']};
                color: white;
                /* 使用Base64编码的SVG，避免路径解析错误 */
                background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxNCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSZNMSA1TDQuNSA4LjVMMTMgMSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=");
                background-repeat: no-repeat;
                background-position: left 10px center;
                padding-left: 28px; /* 对应的padding减小 */
                padding-right: 10px;
                text-align: left;
                border: 1px solid {colors['primary']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_tertiary']};
            }}
            
            /* 次要按钮 */
            QPushButton[secondary="true"] {{
                background-color: {colors['bg_secondary']};
                color: {colors['primary']};
                border: 1px solid {colors['bg_tertiary']};
            }}
            
            QPushButton[secondary="true"]:hover {{
                background-color: {colors['bg_tertiary']};
                border-color: {colors['bg_tertiary']};
            }}

            QPushButton[secondary="true"]:checked {{
                background-color: {colors['primary']};
                color: white;
                border: 1px solid {colors['primary']};
                background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxNCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSZNMSA1TDQuNSA4LjVMMTMgMSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=");
                background-repeat: no-repeat;
                background-position: left 10px center;
                padding-left: 28px;
                padding-right: 10px;
            }}
            
            /* ========== 工具栏 ========== */
            QToolBar {{
                background-color: {colors['bg_secondary']};
                border: none;
                border-bottom: 1px solid {colors['border']};
                spacing: 12px;
                padding: 12px;
            }}
            
            /* ========== 列表样式 ========== */
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0px;
            }}
            
            QListWidget::item {{
                background-color: {colors['bg_secondary']};
                border: none;
                border-radius: 10px;
                padding: 10px 14px; /* 减小间距 */
                margin: 0px 4px 6px 4px;
                color: {colors['text_primary']};
            }}
            
            QListWidget::item:hover {{
                background-color: {colors['bg_elevated']};
            }}
            
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            /* ========== 文本编辑框 ========== */
            QTextEdit, QLineEdit {{
                background-color: {colors['bg_secondary']};
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 10px;
                color: {colors['text_primary']};
                font-size: 13px;
                selection-background-color: {colors['primary']};
            }}
            
            QTextEdit:focus, QLineEdit:focus {{
                background-color: {colors['bg_elevated']};
                border-color: {colors['primary']};
            }}
            
           /* ========== 进度条 ========== */
            QProgressBar {{
                background-color: {colors['bg_tertiary']};
                border: none;
                border-radius: 8px; /* 更圆润 */
                min-height: 16px;   /* 增加高度 */
                max-height: 16px;
                text-align: center;
                color: {colors['text_primary']}; /* 确保文字可见 */
                font-weight: 600;
                font-size: 11px;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors['primary']};
                border-radius: 8px;
            }}
            
            /* ========== 分组框 (类似卡片) ========== */
            QGroupBox {{
                background-color: {colors['bg_secondary']};
                border: 1px solid {colors['border']}; /* 增加微弱边框增加层次 */
                border-radius: 12px;
                margin-top: 10px;
                padding: 16px;
                font-weight: 600;
                color: {colors['text_primary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0px 5px;
                background-color: transparent;
                color: {colors['text_secondary']};
                font-size: 13px;
                font-weight: bold;
            }}
            
            /* ========== 复选框/单选框 ========== */
            QCheckBox {{
                spacing: 8px;
                color: {colors['text_primary']};
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid {colors['separator']};
                background-color: transparent;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
                border-radius: 6px;
                image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxNCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSZNMSA1TDQuNSA4LjVMMTMgMSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=");
            }}

            /* 单选按钮转为开关样式 (Switch) */
            QRadioButton {{
                spacing: 8px;
                color: {colors['text_primary']};
                padding: 4px;
            }}
            
            QRadioButton::indicator {{
                width: 36px;
                height: 20px;
                border-radius: 10px;
                background-color: {colors['bg_tertiary']};
                border: 2px solid {colors['separator']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
            }}

            /* 模拟开关的小圆点 - 使用image属性加载一个圆形SVG */
            QRadioButton::indicator::unchecked {{
                image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8Y2lyY2xlIGN4PSI4IiBjeT0iOCIgcj0iNiIgZmlsbD0iI0FFQUVCMiIvPgo8L3N2Zz4=");
                image-position: left;
            }}
            
            QRadioButton::indicator::checked {{
                image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8Y2lyY2xlIGN4PSI4IiBjeT0iOCIgcj0iNiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
                image-position: right;
            }}
            
            /* ========== 下拉框 ========== */
            QComboBox {{
                background-color: {colors['bg_tertiary']};
                border: 1px solid transparent; 
                border-radius: 8px;
                padding: 6px 12px;
                color: {colors['text_primary']}; /* 修复文字颜色 */
                font-weight: 600;
            }}
            
            QComboBox:hover {{
                background-color: {colors['bg_elevated']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none; /* 暂时隐藏箭头，或者使用Base64箭头 */
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['text_secondary']};
                width: 0;
                height: 0;
                margin-right: 5px;
            }}
            
             /* ========== 菜单栏 ========== */
            QMenuBar {{
                background-color: {colors['bg_secondary']};
                border-bottom: 1px solid {colors['border']};
                color: {colors['text_primary']};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                color: {colors['text_primary']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors['bg_tertiary']};
                border-radius: 6px;
            }}
            
            QMenu {{
                background-color: {colors['bg_elevated']}; /* 确保菜单背景正确 */
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
                color: {colors['text_primary']};
            }}
            
            QMenu::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            /* ========== 状态栏 ========== */
            QStatusBar {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
            }}
            
            /* ========== 滚动条 ========== */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['separator']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QSplitter::handle {{
                background-color: {colors['border']}; /* 给分割线一点颜色，避免完全透明看不见 */
                width: 1px;
            }}
            
            /* ========== 标签页 ========== */
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 10px;
                background-color: {colors['bg_secondary']}; /* 确保Tab内容区域背景正确 */
                top: -1px; 
            }}
            
            QTabWidgetWrapper {{ 
                /* 这是一个不存在的类，但有时这有助于强制刷新 */
                background-color: {colors['bg_primary']};
            }}

            QTabBar::tab {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_secondary']};
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: 600;
                border: 1px solid transparent; 
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['bg_secondary']};
                color: {colors['primary']};
                border-bottom: 2px solid {colors['primary']};
            }}
            
            QTabBar::tab:hover {{
                background-color: {colors['bg_elevated']};
            }}

            /* ========== 滚动区域 ========== */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollArea > QWidget > QWidget {{
                background-color: transparent; /* 让滚动区域内的Widget透明，继承父级 */
            }}
            
            /* ========== 数字输入框 ========== */
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['bg_tertiary']};
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 6px 8px;
                color: {colors['text_primary']};
                font-size: 13px;
                min-height: 24px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                background-color: {colors['bg_elevated']};
                border: 1px solid {colors['primary']};
            }}
            
            /* ========== 标签 ========== */
            QLabel {{
                color: {colors['text_primary']};
                background-color: transparent; /* 防止Label有意外的背景 */
            }}
            
            /* ========== 对话框 ========== */
            QDialog {{
                background-color: {colors['bg_primary']};
            }}
            
            /* 确保Tab页内的Widget背景正确 */
            QDialog QTabWidget QWidget {{
                background-color: {colors['bg_secondary']}; 
            }}

            /* 分组框内的背景 */
            QGroupBox {{
                background-color: {colors['bg_elevated']}; /* 分组框稍微亮一点 */
                border: 1px solid {colors['border']};
                border-radius: 12px;
                margin-top: 10px;
                padding: 16px;
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

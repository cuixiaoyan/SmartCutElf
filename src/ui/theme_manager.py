"""
主题管理器
克制的桌面工具风格
"""

from PyQt5.QtWidgets import QApplication
from typing import Dict


class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self.current_theme = 'light'
        self.themes = {'light': self._get_light_theme()}

    def _get_light_theme(self) -> Dict[str, str]:
        return {
            'accent': '#1677FF',
            'accent_hover': '#0F67E6',
            'accent_pressed': '#0B57C4',
            'success': '#1F9D55',
            'warning': '#B7791F',
            'error': '#D14343',
            'window': '#ECEFF3',
            'panel': '#F6F7F9',
            'surface': '#FFFFFF',
            'surface_alt': '#F8F9FB',
            'surface_hover': '#F3F5F7',
            'selected': '#EAF3FF',
            'text': '#1F2937',
            'text_secondary': '#667085',
            'text_muted': '#98A2B3',
            'text_inverse': '#FFFFFF',
            'border': '#D9DEE5',
            'border_strong': '#C6CDD7',
            'scroll': '#C5CCD6',
        }

    def get_stylesheet(self) -> str:
        c = self.themes[self.current_theme]
        return f"""
            QMainWindow, QDialog {{
                background-color: {c['window']};
            }}

            QWidget {{
                background: transparent;
                color: {c['text']};
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei UI", sans-serif;
                font-size: 13px;
            }}

            QWidget#CentralWidget {{
                background-color: {c['window']};
            }}

            QWidget#TopBar,
            QWidget#RightPanel,
            QWidget#StatsCard,
            QWidget#SettingsShell {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}

            QWidget#TopBar {{
                border-radius: 8px;
            }}

            QWidget#LeftPanel {{
                background-color: {c['panel']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}

            QWidget#ToolbarGroup {{
                background: transparent;
                border: none;
            }}

            QFrame#ToolbarSeparator {{
                background-color: {c['border']};
                border: none;
            }}

            QWidget#SettingsPage,
            QScrollArea#SettingsScroll,
            QScrollArea#SettingsScroll > QWidget > QWidget {{
                background-color: {c['surface']};
            }}

            QFrame#SettingsHeader {{
                background-color: {c['surface']};
                border-bottom: 1px solid {c['border']};
            }}

            QWidget#SettingsBody {{
                background-color: {c['surface']};
            }}

            QFrame#SettingsFooter {{
                background-color: {c['surface']};
                border-top: 1px solid {c['border']};
            }}

            QFrame#SettingsNav {{
                background-color: {c['surface_alt']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}

            QPushButton[settingsNav="true"] {{
                background-color: transparent;
                color: {c['text_secondary']};
                border: 1px solid transparent;
                border-radius: 6px;
                text-align: left;
                padding: 0 12px;
                font-weight: 600;
            }}

            QPushButton[settingsNav="true"]:hover {{
                background-color: {c['surface_hover']};
                color: {c['text']};
            }}

            QPushButton[settingsNav="true"]:checked {{
                background-color: {c['surface']};
                color: {c['accent']};
                border-color: {c['border']};
            }}

            QLabel#HeroTitle {{
                font-size: 18px;
                font-weight: 700;
                color: {c['text']};
            }}

            QLabel#HeroSubtitle {{
                font-size: 12px;
                color: {c['text_secondary']};
            }}

            QLabel#SectionTitle {{
                font-size: 14px;
                font-weight: 700;
                color: {c['text']};
            }}

            QLabel#SectionCaption,
            QLabel[secondary="true"] {{
                color: {c['text_secondary']};
                font-size: 12px;
            }}

            QLabel#ProgressValue {{
                font-size: 20px;
                font-weight: 700;
            }}

            QLabel#StagePill {{
                background-color: {c['surface_alt']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                padding: 4px 9px;
                color: {c['text_secondary']};
                font-size: 12px;
                font-weight: 600;
            }}

            QLabel#StagePill[stage="prepare"],
            QLabel#StagePill[stage="process"],
            QLabel#StagePill[stage="analyze"],
            QLabel#StagePill[stage="edit"],
            QLabel#StagePill[stage="audio"] {{
                background-color: {c['selected']};
                color: {c['accent']};
                border-color: #CFE0FF;
            }}

            QLabel#StagePill[stage="done"] {{
                background-color: #EAF7EF;
                color: {c['success']};
                border-color: #CAE8D4;
            }}

            QLabel#StagePill[stage="warning"],
            QLabel#StagePill[stage="stopping"] {{
                background-color: #FFF6E8;
                color: {c['warning']};
                border-color: #F0D9AF;
            }}

            QPushButton {{
                background-color: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {c['surface_hover']};
                border-color: {c['border_strong']};
            }}

            QPushButton:pressed {{
                background-color: #EDEFF2;
            }}

            QPushButton[primary="true"] {{
                background-color: {c['accent']};
                color: {c['text_inverse']};
                border-color: {c['accent']};
            }}

            QPushButton[primary="true"]:hover {{
                background-color: {c['accent_hover']};
                border-color: {c['accent_hover']};
            }}

            QPushButton[primary="true"]:pressed {{
                background-color: {c['accent_pressed']};
                border-color: {c['accent_pressed']};
            }}

            QPushButton[danger="true"] {{
                background-color: #FDECEC;
                color: {c['error']};
                border-color: #F4C8C8;
            }}

            QPushButton[danger="true"]:hover {{
                background-color: #FBE1E1;
            }}

            QPushButton[toggle="true"] {{
                background-color: transparent;
                color: {c['text_secondary']};
                border-color: transparent;
                border-radius: 4px;
            }}

            QPushButton[toggle="true"]:checked {{
                background-color: {c['surface']};
                border-color: {c['accent']};
                color: {c['accent']};
            }}

            QPushButton[toggle="true"]:hover {{
                background-color: {c['surface_hover']};
                border-color: {c['border']};
            }}

            QPushButton[aiToggle="true"] {{
                background-color: {c['surface_alt']};
                color: {c['text_secondary']};
                border: 1px solid {c['border']};
                border-radius: 15px;
                padding: 0 12px;
                font-weight: 600;
            }}

            QPushButton[aiToggle="true"]:hover {{
                background-color: {c['surface_hover']};
                border-color: {c['border_strong']};
            }}

            QPushButton[aiToggle="true"]:checked {{
                background-color: #F0F7FF;
                color: {c['accent']};
                border-color: #8DBBFF;
            }}

            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {c['text']};
                selection-background-color: #D8E8FF;
            }}

            QComboBox, QSpinBox, QDoubleSpinBox {{
                font-size: 12px;
            }}

            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: #9EC2FF;
            }}

            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                padding: 0;
            }}

            QListWidget::item {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px 12px;
                margin: 0 0 6px 0;
            }}

            QListWidget::item:hover {{
                background-color: {c['surface_hover']};
                border-color: {c['border_strong']};
            }}

            QListWidget::item:selected {{
                background-color: {c['selected']};
                border-color: #CFE0FF;
                color: {c['text']};
            }}

            QProgressBar {{
                background-color: #E6EAF0;
                border: none;
                border-radius: 5px;
                min-height: 10px;
                max-height: 10px;
            }}

            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 5px;
            }}

            QGroupBox {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                margin-top: 8px;
                padding: 10px;
                font-weight: 600;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {c['text_secondary']};
                font-size: 12px;
                font-weight: 700;
            }}

            QFormLayout QLabel {{
                color: {c['text_secondary']};
            }}

            QCheckBox {{
                spacing: 8px;
                color: {c['text']};
                font-weight: 500;
            }}

            QCheckBox::indicator {{
                width: 34px;
                height: 20px;
                border-radius: 10px;
                border: 1px solid {c['border_strong']};
                background-color: #D7DDE5;
            }}

            QCheckBox::indicator:checked {{
                background-color: {c['accent']};
                border-color: {c['accent']};
            }}

            QCheckBox::indicator:unchecked:hover {{
                background-color: #CBD3DD;
            }}

            QComboBox {{
                padding-right: 28px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}

            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {c['text_muted']};
            }}

            QComboBox QAbstractItemView {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                selection-background-color: {c['selected']};
                selection-color: {c['text']};
            }}

            QTabWidget::pane {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                top: -1px;
            }}

            QTabBar::tab {{
                padding: 9px 14px;
                margin: 0 4px 8px 0;
                border-radius: 8px;
                color: {c['text_secondary']};
                background: transparent;
                font-weight: 600;
            }}

            QTabBar::tab:selected {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                color: {c['text']};
            }}

            QTableWidget {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                gridline-color: #EDF1F5;
                alternate-background-color: {c['surface_alt']};
                selection-background-color: {c['selected']};
                selection-color: {c['text']};
            }}

            QHeaderView::section {{
                background-color: {c['surface_alt']};
                color: {c['text_secondary']};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {c['border']};
                font-weight: 700;
            }}

            QMenuBar {{
                background-color: {c['panel']};
                border-bottom: 1px solid {c['border']};
                padding: 4px 8px;
            }}

            QMenuBar::item {{
                padding: 6px 10px;
                border-radius: 8px;
            }}

            QMenuBar::item:selected {{
                background-color: {c['surface']};
            }}

            QMenu {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px;
            }}

            QMenu::item {{
                padding: 8px 12px;
                border-radius: 8px;
            }}

            QMenu::item:selected {{
                background-color: {c['selected']};
            }}

            QStatusBar {{
                background-color: {c['panel']};
                border-top: 1px solid {c['border']};
                color: {c['text_secondary']};
            }}

            QMessageBox {{
                background-color: {c['surface']};
            }}

            QMessageBox QWidget {{
                background-color: {c['surface']};
                color: {c['text']};
            }}

            QMessageBox QLabel {{
                background-color: {c['surface']};
                color: {c['text']};
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 4px;
            }}

            QScrollBar::handle:vertical {{
                background: {c['scroll']};
                border-radius: 5px;
                min-height: 30px;
            }}

            QScrollBar:horizontal {{
                background: transparent;
                height: 10px;
                margin: 4px;
            }}

            QScrollBar::handle:horizontal {{
                background: {c['scroll']};
                border-radius: 5px;
                min-width: 30px;
            }}

            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0;
                height: 0;
            }}

            QSplitter::handle {{
                background: transparent;
                width: 8px;
            }}

            QSplitter::handle:hover {{
                background: #DCE4EE;
                border-radius: 4px;
            }}
        """

    def apply_theme(self, app: QApplication):
        app.setStyleSheet(self.get_stylesheet())

    def get_color(self, color_key: str) -> str:
        return self.themes[self.current_theme].get(color_key, '#000000')


_theme_manager = None


def get_theme_manager() -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

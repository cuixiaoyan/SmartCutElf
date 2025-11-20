"""
增强的UI组件
包括预设选择器、进度显示、快捷操作等
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QGroupBox, QTextEdit, QDialog,
                             QDialogButtonBox, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from pathlib import Path

from utils.config_presets import PresetManager, ConfigPreset
from utils.performance import MemoryMonitor, PerformanceEstimator
from utils.notifications import FileOperations, QuickActions
from utils.error_handler import ErrorSolution


class PresetSelectorWidget(QWidget):
    """预设选择器组件"""
    
    preset_changed = pyqtSignal(str)  # 预设ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title = QLabel('⚙️ 处理模式')
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)
        
        # 预设选择
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumHeight(32)
        
        # 添加预设选项
        for preset_id, preset in PresetManager.PRESETS.items():
            self.preset_combo.addItem(
                f"{preset.icon} {preset.name}",
                preset_id
            )
        
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        layout.addWidget(self.preset_combo)
        
        # 预设说明
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #86868B; font-size: 12px; padding: 4px;")
        layout.addWidget(self.description_label)
        
        # 显示第一个预设的说明
        self._update_description()
    
    def _on_preset_changed(self):
        """预设改变"""
        preset_id = self.preset_combo.currentData()
        self._update_description()
        self.preset_changed.emit(preset_id)
    
    def _update_description(self):
        """更新说明文本"""
        preset_id = self.preset_combo.currentData()
        preset = PresetManager.get_preset(preset_id)
        if preset:
            self.description_label.setText(preset.description)
    
    def get_current_preset_id(self) -> str:
        """获取当前选中的预设ID"""
        return self.preset_combo.currentData()


class EnhancedProgressWidget(QWidget):
    """增强的进度显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.estimator = PerformanceEstimator()
        self.memory_monitor = MemoryMonitor()
        self.start_time = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 进度信息行
        info_layout = QHBoxLayout()
        
        self.status_label = QLabel('等待开始...')
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        
        self.percent_label = QLabel('0%')
        self.percent_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.percent_label)
        
        layout.addLayout(info_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 时间信息行
        time_layout = QHBoxLayout()
        
        self.time_label = QLabel('⏱️ 预估时间: --')
        self.time_label.setStyleSheet("font-size: 11px; color: #86868B;")
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        
        self.memory_label = QLabel('💾 内存: --')
        self.memory_label.setStyleSheet("font-size: 11px; color: #86868B;")
        time_layout.addWidget(self.memory_label)
        
        layout.addLayout(time_layout)
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """更新进度"""
        if total == 0:
            percent = 0
        else:
            percent = int((current / total) * 100)
        
        self.progress_bar.setValue(percent)
        self.percent_label.setText(f'{percent}%')
        self.status_label.setText(message or f'处理中 ({current}/{total})')
        
        # 更新预估时间
        if self.start_time and current > 0:
            import time
            elapsed = time.time() - self.start_time
            avg_time = elapsed / current
            remaining = (total - current) * avg_time
            self.time_label.setText(f'⏱️ 剩余: {self._format_time(remaining)}')
        
        # 更新内存信息
        memory = self.memory_monitor.get_memory_usage()
        percent = memory['system']['percent']
        self.memory_label.setText(f'💾 内存: {percent:.1f}%')
        
        # 内存警告
        if percent > 85:
            self.memory_label.setStyleSheet("font-size: 11px; color: #FF3B30;")
        elif percent > 70:
            self.memory_label.setStyleSheet("font-size: 11px; color: #FF9500;")
        else:
            self.memory_label.setStyleSheet("font-size: 11px; color: #86868B;")
    
    def start_processing(self):
        """开始处理"""
        import time
        self.start_time = time.time()
        self.progress_bar.setValue(0)
        self.status_label.setText('正在处理...')
    
    def finish_processing(self, success: bool = True):
        """完成处理"""
        self.start_time = None
        if success:
            self.progress_bar.setValue(100)
            self.percent_label.setText('100%')
            self.status_label.setText('✅ 处理完成')
        else:
            self.status_label.setText('❌ 处理失败')
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)} 秒"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes} 分 {secs} 秒"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours} 小时 {minutes} 分"


class QuickActionsWidget(QWidget):
    """快捷操作组件"""
    
    open_output_clicked = pyqtSignal()
    copy_log_clicked = pyqtSignal()
    export_log_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 打开输出目录
        self.btn_open_output = QPushButton('📂 打开输出目录')
        self.btn_open_output.setMinimumHeight(32)
        self.btn_open_output.clicked.connect(self.open_output_clicked.emit)
        layout.addWidget(self.btn_open_output)
        
        # 复制日志
        self.btn_copy_log = QPushButton('📋 复制日志')
        self.btn_copy_log.setMinimumHeight(32)
        self.btn_copy_log.clicked.connect(self.copy_log_clicked.emit)
        layout.addWidget(self.btn_copy_log)
        
        # 导出日志
        self.btn_export_log = QPushButton('💾 导出日志')
        self.btn_export_log.setMinimumHeight(32)
        self.btn_export_log.clicked.connect(self.export_log_clicked.emit)
        layout.addWidget(self.btn_export_log)
        
        layout.addStretch()


class ErrorDialog(QDialog):
    """错误对话框"""
    
    def __init__(self, error_code: str, detail: str = "", parent=None):
        super().__init__(parent)
        self.error_code = error_code
        self.detail = detail
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle('错误信息')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 获取错误解决方案
        solution = ErrorSolution.get_solution(self.error_code)
        
        if solution:
            # 标题
            title = QLabel(f"❌ {solution['title']}")
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF3B30;")
            layout.addWidget(title)
            
            # 消息
            message = QLabel(solution['message'])
            message.setWordWrap(True)
            message.setStyleSheet("font-size: 13px; margin: 10px 0;")
            layout.addWidget(message)
            
            # 详细信息
            if self.detail:
                detail_group = QGroupBox("详细信息")
                detail_layout = QVBoxLayout(detail_group)
                detail_text = QTextEdit()
                detail_text.setPlainText(self.detail)
                detail_text.setReadOnly(True)
                detail_text.setMaximumHeight(100)
                detail_layout.addWidget(detail_text)
                layout.addWidget(detail_group)
            
            # 解决方案
            solutions_group = QGroupBox("💡 解决方案")
            solutions_layout = QVBoxLayout(solutions_group)
            
            for i, sol in enumerate(solution['solutions'], 1):
                sol_label = QLabel(f"{i}. {sol}")
                sol_label.setWordWrap(True)
                sol_label.setStyleSheet("margin: 4px 0;")
                solutions_layout.addWidget(sol_label)
            
            layout.addWidget(solutions_group)
            
            # 文档链接
            if solution['doc_link']:
                doc_label = QLabel(f'📖 查看文档: <a href="{solution["doc_link"]}">{solution["doc_link"]}</a>')
                doc_label.setOpenExternalLinks(True)
                doc_label.setStyleSheet("margin: 10px 0;")
                layout.addWidget(doc_label)
        else:
            # 未知错误
            title = QLabel(f"❌ 错误 ({self.error_code})")
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF3B30;")
            layout.addWidget(title)
            
            if self.detail:
                detail_text = QTextEdit()
                detail_text.setPlainText(self.detail)
                detail_text.setReadOnly(True)
                layout.addWidget(detail_text)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class PresetComparisonDialog(QDialog):
    """预设对比对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle('处理模式对比')
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # 说明
        intro = QLabel('选择适合您需求的处理模式：')
        intro.setStyleSheet("font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(intro)
        
        # 预设列表
        for preset_id, preset in PresetManager.PRESETS.items():
            preset_widget = self._create_preset_card(preset)
            layout.addWidget(preset_widget)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_preset_card(self, preset: ConfigPreset) -> QWidget:
        """创建预设卡片"""
        card = QGroupBox(f"{preset.icon} {preset.name}")
        layout = QVBoxLayout(card)
        
        # 描述
        desc = QLabel(preset.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #86868B;")
        layout.addWidget(desc)
        
        # 关键设置
        settings_text = []
        if 'processing.max_workers' in preset.settings:
            settings_text.append(f"并行数: {preset.settings['processing.max_workers']}")
        if 'speech.recognition_model' in preset.settings:
            settings_text.append(f"模型: {preset.settings['speech.recognition_model']}")
        if 'subtitle.enabled' in preset.settings:
            settings_text.append(f"字幕: {'启用' if preset.settings['subtitle.enabled'] else '禁用'}")
        
        if settings_text:
            settings_label = QLabel(" | ".join(settings_text))
            settings_label.setStyleSheet("font-size: 11px; color: #86868B; margin-top: 5px;")
            layout.addWidget(settings_label)
        
        return card

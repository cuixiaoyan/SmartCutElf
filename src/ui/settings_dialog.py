"""
设置对话框模块
提供应用程序的配置界面
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox,
                             QFileDialog, QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.config import get_config

class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        
        # 设置对话框大小为屏幕的一半并居中
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        dialog_width = screen.width() // 2
        dialog_height = screen.height() // 2
        x = (screen.width() - dialog_width) // 2
        y = (screen.height() - dialog_height) //2
        self.setGeometry(x, y, dialog_width, dialog_height)
        
        self._init_ui()
        self._load_settings()
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # 选项卡
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_general_tab(), "常规设置")
        self.tabs.addTab(self._create_processing_tab(), "剪辑设置")
        self.tabs.addTab(self._create_ai_tab(), "AI 模型")
        layout.addWidget(self.tabs)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_save.setMinimumWidth(100)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setMinimumWidth(100)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        self._apply_styles()

    def _create_general_tab(self):
        """创建常规设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输出设置
        group_output = QGroupBox("输出设置")
        form_output = QFormLayout(group_output)
        
        output_layout = QHBoxLayout()
        self.input_output_dir = QLineEdit()
        self.btn_browse_output = QPushButton("浏览...")
        self.btn_browse_output.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.input_output_dir)
        output_layout.addWidget(self.btn_browse_output)
        
        form_output.addRow("输出文件夹:", output_layout)
        
        self.check_auto_open = QCheckBox("处理完成后自动打开文件夹")
        form_output.addRow("", self.check_auto_open)
        
        layout.addWidget(group_output)
        
        # 界面设置
        group_ui = QGroupBox("界面设置")
        form_ui = QFormLayout(group_ui)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light"])
        form_ui.addRow("主题颜色:", self.combo_theme)
        
        layout.addWidget(group_ui)
        layout.addStretch()
        return widget

    def _create_processing_tab(self):
        """创建剪辑设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 视频参数
        group_video = QGroupBox("视频参数")
        form_video = QFormLayout(group_video)
        
        # 时长控制
        group_duration = QGroupBox("时长控制 (秒)")
        form_duration = QFormLayout(group_duration)
        
        self.spin_min_duration = QSpinBox()
        self.spin_min_duration.setRange(10, 3600)
        form_duration.addRow("最小目标时长:", self.spin_min_duration)
        
        self.spin_max_duration = QSpinBox()
        self.spin_max_duration.setRange(10, 3600)
        form_duration.addRow("最大目标时长:", self.spin_max_duration)
        
        self.spin_segment_duration = QSpinBox()
        self.spin_segment_duration.setRange(2, 60)
        form_duration.addRow("单片段时长:", self.spin_segment_duration)
        
        layout.addWidget(group_duration)
        
        # 性能设置
        group_perf = QGroupBox("性能设置")
        form_perf = QFormLayout(group_perf)
        
        self.spin_workers = QSpinBox()
        self.spin_workers.setRange(1, 16)
        form_perf.addRow("并行处理数量:", self.spin_workers)
        
        layout.addWidget(group_perf)
        layout.addStretch()
        return widget

    def _create_ai_tab(self):
        """创建AI设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 语音识别
        group_whisper = QGroupBox("语音识别 (Whisper)")
        form_whisper = QFormLayout(group_whisper)
        
        self.combo_model = QComboBox()
        self.combo_model.addItems(["tiny", "base", "small", "medium", "large"])
        form_whisper.addRow("模型大小:", self.combo_model)
        
        self.check_subtitle = QCheckBox("生成字幕")
        form_whisper.addRow("", self.check_subtitle)
        
        layout.addWidget(group_whisper)
        
        # 高光检测权重
        group_highlight = QGroupBox("高光检测权重")
        form_highlight = QFormLayout(group_highlight)
        
        self.spin_audio_weight = QDoubleSpinBox()
        self.spin_audio_weight.setRange(0, 1)
        self.spin_audio_weight.setSingleStep(0.1)
        form_highlight.addRow("音频权重:", self.spin_audio_weight)
        
        self.spin_video_weight = QDoubleSpinBox()
        self.spin_video_weight.setRange(0, 1)
        self.spin_video_weight.setSingleStep(0.1)
        form_highlight.addRow("视频权重:", self.spin_video_weight)
        
        layout.addWidget(group_highlight)
        layout.addStretch()
        return widget

    def _browse_output_dir(self):
        """浏览输出目录"""
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.input_output_dir.text())
        if path:
            self.input_output_dir.setText(path)

    def _load_settings(self):
        """加载设置"""
        # 常规
        self.input_output_dir.setText(self.config.get('output.folder', 'output'))
        self.check_auto_open.setChecked(self.config.get('output.auto_open', False))
        self.combo_theme.setCurrentText(self.config.get('ui.theme', 'dark'))
        
        # 剪辑
        self.spin_min_duration.setValue(self.config.get('processing.target_duration_min', 180))
        self.spin_max_duration.setValue(self.config.get('processing.target_duration_max', 300))
        self.spin_segment_duration.setValue(self.config.get('processing.segment_duration', 10))
        self.spin_workers.setValue(self.config.get('processing.max_workers', 4))
        
        # AI
        self.combo_model.setCurrentText(self.config.get('speech.recognition_model', 'base'))
        self.check_subtitle.setChecked(self.config.get('subtitle.enabled', True))
        self.spin_audio_weight.setValue(self.config.get('highlight.audio_weight', 0.4))
        self.spin_video_weight.setValue(self.config.get('highlight.video_weight', 0.4))

    def save_settings(self):
        """保存设置"""
        # 常规
        self.config.set('output.folder', self.input_output_dir.text())
        self.config.set('output.auto_open', self.check_auto_open.isChecked())
        self.config.set('ui.theme', self.combo_theme.currentText())
        
        # 剪辑
        self.config.set('processing.target_duration_min', self.spin_min_duration.value())
        self.config.set('processing.target_duration_max', self.spin_max_duration.value())
        self.config.set('processing.segment_duration', self.spin_segment_duration.value())
        self.config.set('processing.max_workers', self.spin_workers.value())
        
        self.config.set('processing.target_duration_min', self.spin_min_duration.value())
        self.config.set('processing.target_duration_max', self.spin_max_duration.value())
        self.config.set('processing.segment_duration', self.spin_segment_duration.value())
        self.config.set('processing.max_workers', self.spin_workers.value())
        
        # AI
        self.config.set('speech.recognition_model', self.combo_model.currentText())
        self.config.set('subtitle.enabled', self.check_subtitle.isChecked())
        self.config.set('highlight.audio_weight', self.spin_audio_weight.value())
        self.config.set('highlight.video_weight', self.spin_video_weight.value())
        
        self.config.save()
        self.accept()
        
    def _apply_styles(self):
        """应用样式"""
        # 移除硬编码样式，使用全局 ThemeManager
        pass

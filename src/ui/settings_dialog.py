"""
设置对话框模块
提供应用程序的配置界面
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox,
                             QFileDialog, QGroupBox, QFormLayout, QMessageBox,
                             QScrollArea, QFrame, QButtonGroup, QStackedWidget,
                             QSizePolicy)
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
        if parent is not None:
            parent_geo = parent.frameGeometry()
            max_width = max(720, parent_geo.width() - 64)
            max_height = max(540, parent_geo.height() - 64)
            dialog_width = min(820, max_width)
            dialog_height = min(620, max_height)
            x = parent_geo.x() + (parent_geo.width() - dialog_width) // 2
            y = parent_geo.y() + (parent_geo.height() - dialog_height) // 2
        else:
            screen = QDesktopWidget().screenGeometry()
            dialog_width = min(max(820, int(screen.width() * 0.56)), max(720, screen.width() - 80))
            dialog_height = min(max(620, int(screen.height() * 0.66)), max(540, screen.height() - 80))
            x = (screen.width() - dialog_width) // 2
            y = (screen.height() - dialog_height) // 2
        self.setGeometry(x, y, dialog_width, dialog_height)
        
        self._init_ui()
        self._load_settings()
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("偏好设置")
        self.setMinimumWidth(720)
        self.setMinimumHeight(520)
        self.setObjectName("SettingsShell")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_frame = QFrame()
        header_frame.setObjectName("SettingsHeader")
        header_frame.setFixedHeight(74)
        header_frame_layout = QVBoxLayout(header_frame)
        header_frame_layout.setContentsMargins(18, 12, 18, 10)
        header_frame_layout.setSpacing(2)
        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel("偏好设置")
        title.setObjectName("HeroTitle")
        header.addWidget(title)
        header.addStretch()

        subtitle = QLabel("调整输出、剪辑节奏、AI 模型与性能策略，让每次批处理更贴近你的素材风格。")
        subtitle.setObjectName("HeroSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_frame_layout.addLayout(header)
        header_frame_layout.addWidget(subtitle)
        layout.addWidget(header_frame)

        body = QWidget()
        body.setObjectName("SettingsBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(14, 12, 14, 12)
        body_layout.setSpacing(0)
        content = QHBoxLayout()
        content.setSpacing(12)

        nav = QFrame()
        nav.setObjectName("SettingsNav")
        nav.setFixedWidth(128)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(6)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        nav_items = [("常规", 0), ("剪辑", 1), ("AI 模型", 2)]
        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("settingsNav", True)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda checked, i=index: self.settings_stack.setCurrentIndex(i))
            self.nav_group.addButton(btn, index)
            nav_layout.addWidget(btn)
            if index == 0:
                btn.setChecked(True)
        nav_layout.addStretch()

        self.settings_stack = QStackedWidget()
        self.settings_stack.addWidget(self._create_general_tab())
        self.settings_stack.addWidget(self._create_processing_tab())
        self.settings_stack.addWidget(self._create_ai_tab())

        content.addWidget(nav)
        content.addWidget(self.settings_stack, 1)
        body_layout.addLayout(content)
        layout.addWidget(body, 1)
        
        # 底部按钮
        footer = QFrame()
        footer.setObjectName("SettingsFooter")
        footer.setFixedHeight(58)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(14, 10, 14, 10)
        btn_layout.setSpacing(8)
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setMinimumWidth(90)
        self.btn_cancel.setProperty("secondary", True)
        
        self.btn_save = QPushButton("保存设置")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_save.setMinimumWidth(90)
        self.btn_save.setProperty("primary", True)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        footer.setLayout(btn_layout)
        layout.addWidget(footer)
        
        self._apply_styles()

    def _create_general_tab(self):
        """创建常规设置标签页"""
        widget = QWidget()
        widget.setObjectName("SettingsPage")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 输出设置
        group_output = QGroupBox("输出设置")
        form_output = QFormLayout(group_output)
        form_output.setSpacing(10)
        form_output.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_output.setContentsMargins(12, 16, 12, 12)
        
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        self.input_output_dir = QLineEdit()
        self.btn_browse_output = QPushButton("浏览...")
        self.btn_browse_output.setMinimumWidth(90)
        self.btn_browse_output.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.input_output_dir)
        output_layout.addWidget(self.btn_browse_output)
        
        form_output.addRow("输出文件夹:", output_layout)
        
        self.check_auto_open = QCheckBox("处理完成后自动打开文件夹")
        form_output.addRow("", self.check_auto_open)

        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(1, 120)
        form_output.addRow("输出帧率:", self.spin_fps)

        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems(["720p", "1080p", "1440p", "2160p"])
        form_output.addRow("输出分辨率:", self.combo_resolution)

        self.input_bitrate = QLineEdit()
        self.input_bitrate.setPlaceholderText("例如 5000k，留空则使用CRF")
        form_output.addRow("视频码率:", self.input_bitrate)
        
        
        layout.addWidget(group_output)
        
        # 环境设置
        group_env = QGroupBox("环境设置")
        form_env = QFormLayout(group_env)
        form_env.setSpacing(10)
        form_env.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_env.setContentsMargins(12, 16, 12, 12)
        
        ffmpeg_layout = QHBoxLayout()
        ffmpeg_layout.setSpacing(8)
        self.input_ffmpeg_path = QLineEdit()
        self.input_ffmpeg_path.setPlaceholderText("系统默认 (自动查找)")
        self.btn_browse_ffmpeg = QPushButton("浏览...")
        self.btn_browse_ffmpeg.setMinimumWidth(90)
        self.btn_browse_ffmpeg.clicked.connect(self._browse_ffmpeg_path)
        ffmpeg_layout.addWidget(self.input_ffmpeg_path)
        ffmpeg_layout.addWidget(self.btn_browse_ffmpeg)
        
        form_env.addRow("FFmpeg 路径:", ffmpeg_layout)
        layout.addWidget(group_env)
        
        # 界面设置 - 已移除
        # ...
        
        layout.addStretch()
        return widget

    def _create_processing_tab(self):
        """创建剪辑设置标签页"""
        scroll = QScrollArea()
        scroll.setObjectName("SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        widget.setObjectName("SettingsPage")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 视频参数
        group_video = QGroupBox("视频参数")
        form_video = QFormLayout(group_video)
        form_video.setSpacing(10)
        form_video.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_video.setContentsMargins(12, 16, 12, 12)
        
        self.combo_orientation = QComboBox()
        self.combo_orientation.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_orientation.addItems(["original", "landscape", "portrait"])
        self.combo_orientation.setItemText(0, "原始比例")
        self.combo_orientation.setItemText(1, "横屏 (1920x1080)")
        self.combo_orientation.setItemText(2, "竖屏 (1080x1920)")
        form_video.addRow("视频比例:", self.combo_orientation)
        
        layout.addWidget(group_video)
        
        # 时长控制
        group_duration = QGroupBox("时长控制（秒）")
        form_duration = QFormLayout(group_duration)
        form_duration.setSpacing(10)
        form_duration.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_duration.setContentsMargins(12, 16, 12, 12)
        
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
        
        # 转场效果设置
        group_transition = QGroupBox("转场效果")
        form_transition = QFormLayout(group_transition)
        form_transition.setSpacing(10)
        form_transition.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_transition.setContentsMargins(12, 16, 12, 12)
        
        self.check_transition_enabled = QCheckBox("启用转场效果")
        form_transition.addRow("", self.check_transition_enabled)
        
        self.combo_transition_type = QComboBox()
        self.combo_transition_type.addItems([
            "fade", "dissolve", "slide_left", "slide_right",
            "slide_up", "slide_down", "zoom_in", "zoom_out",
            "wipe_left", "wipe_right"
        ])
        form_transition.addRow("转场类型:", self.combo_transition_type)
        
        self.spin_transition_duration = QDoubleSpinBox()
        self.spin_transition_duration.setRange(0.1, 2.0)
        self.spin_transition_duration.setSingleStep(0.1)
        self.spin_transition_duration.setSuffix(" 秒")
        form_transition.addRow("转场时长:", self.spin_transition_duration)
        
        layout.addWidget(group_transition)
        
        # 性能设置
        group_perf = QGroupBox("性能设置")
        form_perf = QFormLayout(group_perf)
        form_perf.setSpacing(10)
        form_perf.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_perf.setContentsMargins(12, 16, 12, 12)
        
        self.spin_workers = QSpinBox()
        self.spin_workers.setRange(1, 16)
        form_perf.addRow("并行处理数量:", self.spin_workers)

        self.spin_segment_workers = QSpinBox()
        self.spin_segment_workers.setRange(1, 16)
        form_perf.addRow("单视频片段并发:", self.spin_segment_workers)

        self.spin_ffmpeg_workers = QSpinBox()
        self.spin_ffmpeg_workers.setRange(1, 16)
        form_perf.addRow("FFmpeg全局并发:", self.spin_ffmpeg_workers)
        
        layout.addWidget(group_perf)
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll

    def _create_ai_tab(self):
        """创建AI设置标签页"""
        scroll = QScrollArea()
        scroll.setObjectName("SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        widget.setObjectName("SettingsPage")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 语音识别
        group_whisper = QGroupBox("语音识别（Whisper）")
        form_whisper = QFormLayout(group_whisper)
        form_whisper.setSpacing(10)
        form_whisper.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_whisper.setContentsMargins(12, 16, 12, 12)
        
        self.combo_model = QComboBox()
        self.combo_model.addItems(["tiny", "base", "small", "medium", "large"])
        form_whisper.addRow("模型大小:", self.combo_model)
        
        self.check_ai_enabled = QCheckBox("启用字幕与配音")
        form_whisper.addRow("", self.check_ai_enabled)

        self.check_subtitle_burn_in = QCheckBox("将字幕烧录到视频")
        form_whisper.addRow("", self.check_subtitle_burn_in)
        
        layout.addWidget(group_whisper)
        
        # 配音设置
        group_tts = QGroupBox("配音设置")
        form_tts = QFormLayout(group_tts)
        form_tts.setSpacing(10)
        form_tts.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_tts.setContentsMargins(12, 16, 12, 12)
        
        self.combo_voice = QComboBox()
        self.combo_voice.addItems(["female", "male"])
        form_tts.addRow("配音音色:", self.combo_voice)
        
        self.check_bgm = QCheckBox("启用背景音乐")
        form_tts.addRow("", self.check_bgm)
        
        self.spin_volume = QSpinBox()
        self.spin_volume.setRange(0, 100)
        self.spin_volume.setSuffix("%")
        form_tts.addRow("音乐音量:", self.spin_volume)
        
        layout.addWidget(group_tts)
        
        # 高光检测权重
        group_highlight = QGroupBox("高光检测权重")
        form_highlight = QFormLayout(group_highlight)
        form_highlight.setSpacing(10)
        form_highlight.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_highlight.setContentsMargins(12, 16, 12, 12)
        
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
        
        scroll.setWidget(widget)
        return scroll

    def _browse_output_dir(self):
        """浏览输出目录"""
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.input_output_dir.text())
        if path:
            self.input_output_dir.setText(path)

    def _browse_ffmpeg_path(self):
        """浏览FFmpeg可执行文件"""
        file, _ = QFileDialog.getOpenFileName(self, "选择 FFmpeg 可执行文件", "", "Executables (*.exe);;All Files (*)")
        if file:
            self.input_ffmpeg_path.setText(file)

    def _load_settings(self):
        """加载设置"""
        self.input_output_dir.setText(self.config.get('output.folder', 'output'))
        self.check_auto_open.setChecked(self.config.get('output.auto_open', False))
        self.spin_fps.setValue(self.config.get('output.fps', 30))
        self.combo_resolution.setCurrentText(self.config.get('output.resolution', '1080p'))
        self.input_bitrate.setText(str(self.config.get('output.bitrate', '')))
        
        # 环境
        self.input_ffmpeg_path.setText(self.config.get('paths.ffmpeg', ''))
        
        # self.combo_theme.setCurrentText(self.config.get('ui.theme', 'dark'))
        
        # 剪辑
        self.combo_orientation.setCurrentText(self.config.get('processing.orientation', 'original'))
        # 由于我们设置了显示文本，需要特殊处理一下回显，或者直接存储英文值
        # 这里简化处理，通过查找匹配的英文值来设置索引
        orientation = self.config.get('processing.orientation', 'original')
        index = self.combo_orientation.findText(orientation, Qt.MatchContains) # 这种方式可能不准，因为我们改了显示文本
        # 更稳妥的方式是根据值手动设置
        if orientation == 'landscape':
            self.combo_orientation.setCurrentIndex(1)
        elif orientation == 'portrait':
            self.combo_orientation.setCurrentIndex(2)
        else:
            self.combo_orientation.setCurrentIndex(0)

        self.spin_min_duration.setValue(self.config.get('processing.target_duration_min', 180))
        self.spin_max_duration.setValue(self.config.get('processing.target_duration_max', 300))
        self.spin_segment_duration.setValue(self.config.get('processing.segment_duration', 10))
        
        # 转场效果
        self.check_transition_enabled.setChecked(self.config.get('processing.transition_enabled', True))
        self.combo_transition_type.setCurrentText(self.config.get('processing.transition_type', 'fade'))
        self.spin_transition_duration.setValue(self.config.get('processing.transition_duration', 0.5))
        
        self.spin_workers.setValue(self.config.get('processing.max_workers', 2))
        self.spin_segment_workers.setValue(self.config.get('processing.max_segment_workers', 2))
        self.spin_ffmpeg_workers.setValue(self.config.get('processing.max_ffmpeg_workers', 2))
        
        # AI
        self.combo_model.setCurrentText(self.config.get('speech.recognition_model', 'base'))
        
        is_enabled = self.config.get('subtitle.enabled', True) or self.config.get('speech.tts_enabled', False)
        self.check_ai_enabled.setChecked(is_enabled)
        self.check_subtitle_burn_in.setChecked(self.config.get('subtitle.burn_in', False))
        
        self.combo_voice.setCurrentText(self.config.get('speech.tts_voice', 'female'))
        self.check_bgm.setChecked(self.config.get('speech.background_music', False))
        self.spin_volume.setValue(self.config.get('speech.music_volume', 30))
        
        self.spin_audio_weight.setValue(self.config.get('highlight.audio_weight', 0.4))
        self.spin_video_weight.setValue(self.config.get('highlight.video_weight', 0.4))

    def save_settings(self):
        """保存设置"""
        # 常规
        self.config.set('output.folder', self.input_output_dir.text())
        self.config.set('output.auto_open', self.check_auto_open.isChecked())
        self.config.set('output.fps', self.spin_fps.value())
        self.config.set('output.resolution', self.combo_resolution.currentText())
        self.config.set('output.bitrate', self.input_bitrate.text().strip())
        
        # 环境
        ffmpeg_path = self.input_ffmpeg_path.text().strip()
        if ffmpeg_path:
            self.config.set('paths.ffmpeg', ffmpeg_path)
        else:
            # 如果清空了，可以移除配置或者设为空字符串
             self.config.set('paths.ffmpeg', '')
             
        # self.config.set('ui.theme', self.combo_theme.currentText())
        
        # 剪辑
        # 获取选中的值
        orientation_idx = self.combo_orientation.currentIndex()
        orientation_val = 'original'
        if orientation_idx == 1:
            orientation_val = 'landscape'
        elif orientation_idx == 2:
            orientation_val = 'portrait'
        self.config.set('processing.orientation', orientation_val)
        
        self.config.set('processing.target_duration_min', self.spin_min_duration.value())
        self.config.set('processing.target_duration_max', self.spin_max_duration.value())
        self.config.set('processing.segment_duration', self.spin_segment_duration.value())
        
        # 转场效果
        self.config.set('processing.transition_enabled', self.check_transition_enabled.isChecked())
        self.config.set('processing.transition_type', self.combo_transition_type.currentText())
        self.config.set('processing.transition_duration', self.spin_transition_duration.value())
        
        self.config.set('processing.max_workers', self.spin_workers.value())
        self.config.set('processing.max_segment_workers', self.spin_segment_workers.value())
        self.config.set('processing.max_ffmpeg_workers', self.spin_ffmpeg_workers.value())
        
        # AI
        self.config.set('speech.recognition_model', self.combo_model.currentText())
        
        is_enabled = self.check_ai_enabled.isChecked()
        self.config.set('subtitle.enabled', is_enabled)
        self.config.set('speech.tts_enabled', is_enabled)
        self.config.set('subtitle.burn_in', self.check_subtitle_burn_in.isChecked())
        
        self.config.set('speech.tts_voice', self.combo_voice.currentText())
        self.config.set('speech.background_music', self.check_bgm.isChecked())
        self.config.set('speech.music_volume', self.spin_volume.value())
        
        self.config.set('highlight.audio_weight', self.spin_audio_weight.value())
        self.config.set('highlight.video_weight', self.spin_video_weight.value())
        
        self.config.save()
        self.accept()
        
    def _apply_styles(self):
        """应用样式"""
        # 移除硬编码样式，使用全局 ThemeManager
        pass

"""
临时保存当前的toolbar创建方法，用于重构
"""

def _create_toolbar_new(self) -> QHBoxLayout:
    """创建工具栏 - 分组布局"""
    from PyQt5.QtWidgets import QFrame, QButtonGroup
    toolbar = QHBoxLayout()
    toolbar.setSpacing(8)

    # ============ 主要操作组 ============
    self.btn_open = QPushButton('📂 打开')
    self.btn_open.setMinimumWidth(90)
    self.btn_open.setToolTip('选择包含视频文件的文件夹')
    self.btn_open.clicked.connect(self.open_folder)
    toolbar.addWidget(self.btn_open)

    self.btn_start = QPushButton('▶️ 开始处理')
    self.btn_start.setMinimumWidth(100)
    self.btn_start.setProperty("primary", True)
    self.btn_start.setEnabled(False)
    self.btn_start.setToolTip('开始处理视频文件')
    self.btn_start.clicked.connect(self.start_processing)
    toolbar.addWidget(self.btn_start)

    self.btn_stop = QPushButton('⏹ 停止')
    self.btn_stop.setMinimumWidth(70)
    self.btn_stop.setEnabled(False)
    self.btn_stop.setToolTip('停止当前处理')
    self.btn_stop.clicked.connect(self.stop_processing)
    toolbar.addWidget(self.btn_stop)

    toolbar.addSpacing(16)

    # 添加第一组分隔线
    separator1 = QFrame()
    separator1.setFrameShape(QFrame.VLine)
    separator1.setFixedHeight(24)
    separator1.setStyleSheet("background-color: #E5E5EA; margin: 0 8px;")
    toolbar.addWidget(separator1)

    # ============ 处理选项组 ============
    options_label = QLabel('选项:')
    options_label.setStyleSheet("color: #86868B; font-size: 12px;")
    toolbar.addWidget(options_label)

    self.chk_ai_enabled = QCheckBox('🎙️ 字幕+配音')
    is_enabled = self.config.get('subtitle.enabled', True) or self.config.get('speech.tts_enabled', False)
    self.chk_ai_enabled.setChecked(is_enabled)
    self.chk_ai_enabled.setToolTip('启用语音识别和AI配音功能')
    toolbar.addWidget(self.chk_ai_enabled)

    toolbar.addSpacing(16)

    # 添加第二组分隔线
    separator2 = QFrame()
    separator2.setFrameShape(QFrame.VLine)
    separator2.setFixedHeight(24)
    separator2.setStyleSheet("background-color: #E5E5EA; margin: 0 8px;")
    toolbar.addWidget(separator2)

    # ============ 预设配置组 ============
    preset_label = QLabel('预设:')
    preset_label.setStyleSheet("color: #86868B; font-size: 12px;")
    toolbar.addWidget(preset_label)

    self.preset_group = QButtonGroup(self)
    self.preset_group.setExclusive(True)

    self.btn_preset_std = QPushButton('标准')
    self.btn_preset_std.setFixedWidth(70)
    self.btn_preset_std.setCheckable(True)
    self.btn_preset_std.setChecked(True)
    self.btn_preset_std.setToolTip('标准模式：平衡质量与速度')
    self.btn_preset_std.clicked.connect(lambda: self.on_preset_changed('标准'))
    self.preset_group.addButton(self.btn_preset_std)
    toolbar.addWidget(self.btn_preset_std)

    self.btn_preset_fast = QPushButton('快速')
    self.btn_preset_fast.setFixedWidth(70)
    self.btn_preset_fast.setCheckable(True)
    self.btn_preset_fast.setProperty("secondary", True)
    self.btn_preset_fast.setToolTip('快速模式：快速预览，降低质量')
    self.btn_preset_fast.clicked.connect(lambda: self.on_preset_changed('快速'))
    self.preset_group.addButton(self.btn_preset_fast)
    toolbar.addWidget(self.btn_preset_fast)

    self.preset_group.buttonClicked.connect(self._update_preset_buttons)

    toolbar.addSpacing(12)

    # ============ 视频类型组 ============
    type_label = QLabel('类型:')
    type_label.setStyleSheet("color: #86868B; font-size: 12px;")
    toolbar.addWidget(type_label)

    from PyQt5.QtWidgets import QComboBox
    self.combo_video_type = QComboBox()
    self.combo_video_type.addItem("🔍 自动", "auto")
    self.combo_video_type.addItem("🎮 游戏", "game")
    self.combo_video_type.addItem("📹 Vlog", "vlog")
    self.combo_video_type.addItem("📚 教育", "education")
    self.combo_video_type.addItem("⚽ 体育", "sports")
    self.combo_video_type.addItem("💬 访谈", "talk")
    self.combo_video_type.addItem("🎵 音乐", "music")
    self.combo_video_type.setCurrentIndex(0)
    self.combo_video_type.setFixedWidth(100)
    self.combo_video_type.setToolTip('选择视频类型以优化检测策略')
    toolbar.addWidget(self.combo_video_type)

    toolbar.addStretch()

    # ============ 其他操作组 ============
    self.btn_settings = QPushButton('⚙️')
    self.btn_settings.setFixedWidth(40)
    self.btn_settings.setProperty("secondary", True)
    self.btn_settings.setToolTip('打开设置')
    self.btn_settings.clicked.connect(self.open_settings)
    toolbar.addWidget(self.btn_settings)

    return toolbar

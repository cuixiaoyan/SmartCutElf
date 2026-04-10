"""
主窗口
SmartCutElf的主用户界面
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QListWidget,
                             QProgressBar, QTextEdit, QSplitter, QStatusBar, QMessageBox, QListWidgetItem,
                             QGroupBox, QCheckBox, QDialog, QApplication, QRadioButton,
                             QButtonGroup, QFrame, QStackedWidget, QSizePolicy,
                             QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QMimeData, QUrl, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtGui import QIcon, QFont
from pathlib import Path
from datetime import datetime
from utils.config import get_config
from utils.logger import setup_logger
from utils.file_manager import FileManager
from core.workflow import VideoProcessingWorkflow
from ui.theme_manager import get_theme_manager


class ProcessingThread(QThread):
    """视频处理线程"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(list)  # results

    def __init__(self, workflow, video_files, video_type=None):
        super().__init__()
        self.workflow = workflow
        self.video_files = video_files
        self.video_type = video_type

    def run(self):
        """运行处理"""
        def progress_callback(current, total, message):
            self.progress.emit(current, total, message)

        results = self.workflow.process_batch(
            [f['path'] for f in self.video_files],
            video_type=self.video_type,
            callback=progress_callback
        )
        self.finished.emit(results)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        self.config = get_config()
        self.logger = setup_logger()
        self.file_manager = FileManager()
        self.workflow = VideoProcessingWorkflow()
        self.theme_manager = get_theme_manager()

        self.video_files = []
        self.current_project_id = None
        self.processing_thread = None
        self._animations = []
        self._last_stage = "idle"

        # 内存监控
        from utils.memory_monitor import get_memory_monitor
        self.memory_monitor = get_memory_monitor()

        # 启用拖放功能
        self.setAcceptDrops(True)

        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("SmartCutElf - 智剪精灵 v1.0")

        # 获取屏幕尺寸并计算窗口大小（1/4屏幕面积，即宽高各为屏幕的1/2）
        screen = QApplication.primaryScreen().geometry()
        width = screen.width() // 2
        height = screen.height() // 2

        # 计算居中位置 (稍微向上偏移一点，视觉上更舒适)
        x = (screen.width() - width) // 2
        y = max(0, (screen.height() - height) // 2 - 100)

        self.setGeometry(x, y, width, height)
        self.setMinimumSize(1000, 700)  # 设置一个合理的最小尺寸

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent.parent / 'assets' / 'app_icon.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            self.logger.info(f"窗口图标已设置: {icon_path}")
        else:
            self.logger.warning(f"图标文件不存在: {icon_path}")

        # 创建中央部件
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 10, 14, 14)
        main_layout.setSpacing(10)

        # 顶部工具栏
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # 分割器（左侧文件列表，右侧预览区域）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧面板
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # 右侧面板
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # 设置分割器比例 - 左侧占30%
        # 窗口总宽 width，左侧 width * 0.3
        left_width = int(width * 0.3)
        right_width = width - left_width
        splitter.setSizes([left_width, right_width])
        main_layout.addWidget(splitter)

        # 底部状态栏
        self._create_status_bar()

    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        container = QWidget()
        container.setObjectName("TopBar")
        container.setFixedHeight(42)

        toolbar = QHBoxLayout(container)
        toolbar.setSpacing(6)
        toolbar.setContentsMargins(6, 3, 6, 3)

        action_group = QFrame()
        action_group.setObjectName("ToolbarGroup")
        action_layout = QHBoxLayout(action_group)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        action_group.setMinimumWidth(320)

        # 统一按钮尺寸
        btn_w, btn_h = 88, 28

        # 开始处理按钮
        self.btn_start = QPushButton('开始生成')
        self.btn_start.setFixedHeight(btn_h)
        self.btn_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_start.setProperty("primary", True)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_processing)
        action_layout.addWidget(self.btn_start)

        # 停止按钮
        self.btn_stop = QPushButton('停止')
        self.btn_stop.setFixedSize(64, btn_h)
        self.btn_stop.setProperty("danger", True)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)
        action_layout.addWidget(self.btn_stop)

        toolbar.addWidget(action_group)

        toolbar.addSpacing(8)

        option_group = QFrame()
        option_group.setObjectName("ToolbarGroup")
        option_layout = QHBoxLayout(option_group)
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setSpacing(8)

        # 字幕+配音开关
        self.chk_ai_enabled = QCheckBox('字幕+配音')
        is_enabled = self.config.get('subtitle.enabled', True) or self.config.get('speech.tts_enabled', False)
        self.chk_ai_enabled.setChecked(is_enabled)
        option_layout.addWidget(self.chk_ai_enabled)

        # 预设选择
        from PyQt5.QtWidgets import QButtonGroup
        preset_label = QLabel('模式')
        preset_label.setProperty("secondary", True)
        option_layout.addWidget(preset_label)

        self.preset_group = QButtonGroup(self)
        self.preset_group.setExclusive(True)

        # 预设按钮
        preset_configs = [('标准', 'std'), ('快速', 'fast')]
        for display_name, key in preset_configs:
            btn = QPushButton(display_name)
            btn.setFixedSize(68, btn_h)
            btn.setCheckable(True)
            btn.setProperty("toggle", True)
            if display_name == '标准':
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, n=display_name: self.on_preset_changed(n))
            self.preset_group.addButton(btn)
            option_layout.addWidget(btn)
            setattr(self, f'btn_preset_{key}', btn)

        self.preset_group.buttonClicked.connect(self._update_preset_buttons)

        # 视频类型选择
        from PyQt5.QtWidgets import QComboBox
        type_label = QLabel('内容类型')
        type_label.setProperty("secondary", True)
        option_layout.addWidget(type_label)

        self.combo_video_type = QComboBox()
        self.combo_video_type.addItem("自动检测", "auto")
        self.combo_video_type.addItem("游戏", "game")
        self.combo_video_type.addItem("Vlog", "vlog")
        self.combo_video_type.addItem("教育", "education")
        self.combo_video_type.addItem("体育", "sports")
        self.combo_video_type.addItem("访谈", "talk")
        self.combo_video_type.addItem("音乐", "music")
        self.combo_video_type.addItem("通用", "generic")
        self.combo_video_type.setCurrentIndex(0)
        self.combo_video_type.setFixedHeight(btn_h)
        self.combo_video_type.setMinimumWidth(96)
        option_layout.addWidget(self.combo_video_type)

        toolbar.addWidget(option_group)

        toolbar.addStretch()

        self.btn_settings = QPushButton('设置')
        self.btn_settings.setFixedSize(60, btn_h)
        self.btn_settings.setToolTip('打开设置')
        self.btn_settings.clicked.connect(self.open_settings)
        toolbar.addWidget(self.btn_settings)

        return container

    def _create_left_panel(self) -> QWidget:
        """创建左侧文件列表面板"""
        panel = QWidget()
        panel.setObjectName("LeftPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 标题区域
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title = QLabel('视频文件列表')
        title.setObjectName("SectionTitle")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # 文件数量标签
        self.file_count_label = QLabel('0 个文件')
        self.file_count_label.setObjectName("SectionCaption")
        title_layout.addWidget(self.file_count_label)

        layout.addLayout(title_layout)

        # 文件列表
        self.file_stack = QStackedWidget()

        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        self.file_list.currentItemChanged.connect(self.on_file_selected)

        self.empty_files_state = self._create_empty_state(
            "还没有视频目录",
            "打开一个包含视频的目录后，这里会显示待处理文件。\n也支持直接拖放视频文件到窗口中。",
            "打开目录",
            self.open_folder
        )

        self.file_stack.addWidget(self.empty_files_state)
        self.file_stack.addWidget(self.file_list)
        self.file_stack.setCurrentWidget(self.empty_files_state)
        layout.addWidget(self.file_stack)

        # 文件说明
        self.file_info_label = QLabel('请选择文件夹以加载视频')
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setProperty("secondary", True)
        layout.addWidget(self.file_info_label)

        return panel

    def _create_right_panel(self) -> QWidget:
        """创建右侧预览面板"""
        panel = QWidget()
        panel.setObjectName("RightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 标题
        title = QLabel('处理状态与进度')
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        stage_row = QHBoxLayout()
        stage_row.setSpacing(6)
        self.stage_label = QLabel("待开始")
        self.stage_label.setObjectName("StagePill")
        stage_row.addWidget(self.stage_label)
        self.status_banner = QLabel("准备就绪")
        self.status_banner.setObjectName("SectionCaption")
        stage_row.addWidget(self.status_banner)
        stage_row.addStretch()
        layout.addLayout(stage_row)

        stats_card = QWidget()
        stats_card.setObjectName("StatsCard")
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self.progress_label = QLabel('等待开始...')
        self.progress_label.setProperty("secondary", True)
        top_row.addWidget(self.progress_label)
        top_row.addStretch()

        self.progress_percent_label = QLabel('0%')
        self.progress_percent_label.setObjectName("ProgressValue")
        top_row.addWidget(self.progress_percent_label)

        stats_layout.addLayout(top_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        stats_layout.addWidget(self.progress_bar)

        layout.addWidget(stats_card)

        # 状态日志标题
        log_title = QLabel('处理日志')
        log_title.setObjectName("SectionCaption")
        layout.addWidget(log_title)

        # 状态文本
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText('准备就绪。\n\n从左上角导入一个目录，选择模式与内容类型，然后开始生成。处理日志会在这里按时间展开。')
        self.status_text.setFont(QFont('SF Mono', 10))
        layout.addWidget(self.status_text)

        # 快捷操作按钮
        from ui.enhanced_widgets import QuickActionsWidget
        quick_actions = QuickActionsWidget()
        quick_actions.open_output_clicked.connect(self.open_output_folder)
        quick_actions.copy_log_clicked.connect(self.copy_log_to_clipboard)
        quick_actions.export_log_clicked.connect(self.export_log)
        layout.addWidget(quick_actions)

        self.progress_card = stats_card

        return panel

    def _create_empty_state(self, title_text: str, body_text: str, button_text: str, callback) -> QWidget:
        """创建空状态卡片"""
        from ui.enhanced_widgets import GuidedEmptyState
        card = GuidedEmptyState(title_text, body_text, button_text, callback)
        card.setObjectName("StatsCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return card

    def _infer_stage(self, message: str) -> tuple[str, str]:
        """从进度文本推断阶段"""
        text = (message or "").lower()
        if any(k in text for k in ["扫描", "准备", "目录", "素材"]):
            return "prepare", "准备素材"
        if any(k in text for k in ["分析", "高光", "识别", "detect"]):
            return "analyze", "分析内容"
        if any(k in text for k in ["剪辑", "片段", "合并", "concat", "cut"]):
            return "edit", "剪辑合成"
        if any(k in text for k in ["字幕", "配音", "音频", "tts"]):
            return "audio", "字幕与音频"
        if any(k in text for k in ["完成", "输出", "导出"]):
            return "done", "输出完成"
        return "process", "处理中"

    def _set_stage(self, stage_key: str, stage_text: str):
        """更新阶段标签样式和文本"""
        self._last_stage = stage_key
        self.stage_label.setText(stage_text)
        self.stage_label.setProperty("stage", stage_key)
        self.stage_label.style().unpolish(self.stage_label)
        self.stage_label.style().polish(self.stage_label)

    def _fade_widget(self, widget: QWidget, start: float = 0.0, end: float = 1.0, duration: int = 320):
        """对控件执行轻量淡入动画"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(lambda: self._animations.remove(animation) if animation in self._animations else None)
        self._animations.append(animation)
        animation.start()

    def _pulse_progress_card(self):
        """处理过程中轻微强调进度卡片"""
        if not hasattr(self, 'progress_card'):
            return
        self._fade_widget(self.progress_card, 0.72, 1.0, 260)

    def _show_completion_feedback(self, success_count: int, failed_count: int):
        """完成态反馈"""
        if failed_count == 0:
            self.status_banner.setText(f"已完成 {success_count} 个视频，结果已整理好。")
            self._set_stage("done", "全部完成")
        else:
            self.status_banner.setText(f"处理结束，成功 {success_count} 个，失败 {failed_count} 个。")
            self._set_stage("warning", "部分完成")
        self._fade_widget(self.status_banner, 0.2, 1.0, 420)
        self._fade_widget(self.progress_card, 0.45, 1.0, 420)

    def open_output_folder(self):
        """打开输出文件夹"""
        output_dir = self.config.get('output.folder', 'output')
        output_path = Path(output_dir)

        if output_path.exists():
            import os
            import subprocess
            import sys

            # 使用系统命令打开文件夹
            if sys.platform == 'win32':
                os.startfile(str(output_path))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(output_path)])
            else:
                subprocess.run(['xdg-open', str(output_path)])
            self.add_status_message(f"已打开输出目录: {output_path}")
        else:
            self.add_status_message(f"输出目录不存在: {output_path}")

    def copy_log_to_clipboard(self):
        """复制日志到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.status_text.toPlainText())
        self.add_status_message("日志已复制到剪贴板")

    def export_log(self):
        """导出日志到文件"""
        from PyQt5.QtWidgets import QFileDialog
        from datetime import datetime

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '导出日志',
            f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            '文本文件 (*.txt);;所有文件 (*)'
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.status_text.toPlainText())
                self.add_status_message(f"日志已导出: {file_path}")
            except Exception as e:
                self.add_status_message(f"导出失败: {e}")

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')

        # 添加内存显示
        self.memory_label = QLabel()
        self.status_bar.addPermanentWidget(self.memory_label)

        # 启动内存监控定时器
        from PyQt5.QtCore import QTimer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self._update_memory_label)
        self.memory_timer.start(2000)  # 每2秒更新一次

    def _update_memory_label(self):
        """更新内存使用标签"""
        memory_str = self.memory_monitor.get_memory_str()
        self.memory_label.setText(f'内存: {memory_str}')

    def _apply_theme(self):
        """应用主题"""
        self.theme_manager.apply_theme(QApplication.instance())
        self._update_preset_buttons()

    def _update_preset_buttons(self, _=None):
        """更新预设按钮的样式"""
        for btn in self.preset_group.buttons():
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def on_preset_changed(self, preset_name: str):
        """配置预设改变"""
        self.add_status_message(f"切换到{preset_name}模式")

        # 根据预设调整配置
        if preset_name == '标准':
            self.config.set('highlight.sensitivity', 0.6, permanent=True)
            self.config.set('highlight.min_duration', 3.0, permanent=True)
        elif preset_name == '快速':
            self.config.set('highlight.sensitivity', 0.4, permanent=True)
            self.config.set('highlight.min_duration', 2.0, permanent=True)

    def open_folder(self):
        """打开文件夹并加载视频"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            '选择视频文件夹',
            ''
        )

        if folder_path:
            self.load_videos(Path(folder_path))

    def load_videos(self, folder_path: Path):
        """加载视频文件"""
        self.add_status_message(f"正在扫描文件夹: {folder_path}")
        self.video_files = []
        self.file_list.clear()

        # 获取支持的视频文件
        supported_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
        files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]

        if not files:
            self.file_stack.setCurrentWidget(self.empty_files_state)
            self.file_info_label.setText("未找到支持的视频文件")
            self.add_status_message("未找到支持的视频文件")
            self._set_stage("idle", "待开始")
            return

        total_size = 0
        for i, video_file in enumerate(files, 1):
            try:
                stat = video_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                total_size += size_mb

                self.video_files.append({
                    'name': video_file.name,
                    'path': str(video_file),
                    'size': stat.st_size,
                    'size_mb': size_mb,
                    'extension': video_file.suffix[1:].upper(),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
            except Exception as e:
                self.logger.warning(f"无法读取文件 {video_file}: {e}")

        # 更新文件列表
        for i, video_file in enumerate(self.video_files, 1):
            size_mb = video_file['size_mb']
            # 限制文件名长度，避免换行
            name = video_file['name']
            if len(name) > 30:
                name = name[:27] + "..."
            item_text = f"{i}. {name}\n   {size_mb:.1f} MB | {video_file['extension']}"
            item = QListWidgetItem(item_text)
            self.file_list.addItem(item)

        # 更新统计信息
        count = len(self.video_files)
        self.file_count_label.setText(f"{count} 个文件")

        if count > 0:
            self.file_stack.setCurrentWidget(self.file_list)
            stats = f"扫描完成！\n\n文件数量: {count}\n总大小: {total_size:.1f} MB\n平均大小: {total_size/count:.1f} MB"
            self.file_info_label.setText(stats)
            self.add_status_message(f"找到 {count} 个视频文件，总大小 {total_size:.1f} MB")
            self.status_bar.showMessage(f"已加载 {count} 个视频文件 | 总大小 {total_size:.1f} MB")
            self.btn_start.setEnabled(True)
            self.status_banner.setText("素材已准备好")
            self._set_stage("ready", "等待开始")
            self._fade_widget(self.file_list, 0.0, 1.0, 260)
        else:
            self.file_stack.setCurrentWidget(self.empty_files_state)
            self.file_info_label.setText("未找到支持的视频文件")
            self.add_status_message("未找到支持的视频文件")
            self.status_bar.showMessage("未找到视频文件")

        self.add_status_message(f"{'='*60}\n")

    def start_processing(self):
        """开始处理视频"""
        if not self.video_files:
            QMessageBox.warning(self, '警告', '请先选择视频文件夹')
            return

        ai_enabled = self.chk_ai_enabled.isChecked()
        self.config.set('subtitle.enabled', ai_enabled)
        self.config.set('speech.tts_enabled', ai_enabled)
        self.config.save()

        self.add_status_message(f"字幕与配音: {'启用' if ai_enabled else '禁用'}")
        self.status_banner.setText("准备中")
        self._set_stage("prepare", "准备素材")

        # 获取选择的视频类型
        video_type_data = self.combo_video_type.currentData()
        video_type_name = self.combo_video_type.currentText()
        if video_type_data != "auto":
            self.add_status_message(f"视频类型: {video_type_name}")

        self.add_status_message("="*60 + "\n")

        # 禁用按钮
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.chk_ai_enabled.setEnabled(False)
        self.combo_video_type.setEnabled(False)

        # 创建处理线程
        self.processing_thread = ProcessingThread(
            self.workflow,
            self.video_files,
            video_type=video_type_data if video_type_data != "auto" else None
        )
        self.processing_thread.progress.connect(self.on_processing_progress)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()

        self.add_status_message("开始处理...\n")
        self._fade_widget(self.progress_card, 0.4, 1.0, 360)

    def stop_processing(self):
        """停止处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                '确认停止',
                '确定要停止当前处理吗？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.logger.info("用户请求停止处理")
                self.add_status_message("\n正在停止处理...")
                self.status_banner.setText("停止中")
                self._set_stage("stopping", "正在停止")
                self.workflow.stop_processing()
                self.processing_thread.wait()

        # 恢复按钮状态
        self.btn_start.setEnabled(len(self.video_files) > 0)
        self.btn_stop.setEnabled(False)
        self.chk_ai_enabled.setEnabled(True)
        self.combo_video_type.setEnabled(True)

    def on_processing_progress(self, current: int, total: int, message: str):
        """处理进度更新"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        self.progress_percent_label.setText(f'{progress}%')
        stage_key, stage_text = self._infer_stage(message)
        self._set_stage(stage_key, stage_text)
        self.status_banner.setText(stage_text)
        self._pulse_progress_card()
        self.add_status_message(f"[{current}/{total}] {message}")

    def on_processing_finished(self, results: list):
        """处理完成"""
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = len(results) - success_count

        self.add_status_message("\n" + "="*60)
        self.add_status_message("批量处理完成！")
        self.add_status_message(f"统计信息:")
        self.add_status_message(f"   • 成功: {success_count} 个")
        self.add_status_message(f"   • 失败: {failed_count} 个")
        self.add_status_message(f"   • 总计: {len(results)} 个")

        # 显示成功的文件
        if success_count > 0:
            self.add_status_message(f"\n成功处理的文件:")
            for i, result in enumerate([r for r in results if r.get('success')], 1):
                output_file = Path(result['output_path']).name
                duration = result.get('total_duration', 0)
                time_taken = result.get('processing_time', 0)
                self.add_status_message(f"   {i}. {output_file} | 时长: {duration:.1f}s | 耗时: {time_taken:.1f}s")

        # 显示失败的文件
        if failed_count > 0:
            self.add_status_message(f"\n处理失败的文件:")
            for i, result in enumerate([r for r in results if not r.get('success')], 1):
                input_file = Path(result.get('input_path', '未知文件')).name if result.get('input_path') else '未知文件'
                error = result.get('error', '未知错误')
                self.add_status_message(f"   {i}. {input_file} - {error}")

        self.add_status_message(f"\n输出目录: {self.config.get('output.folder', 'output')}")
        self.add_status_message("="*60 + "\n")

        # 更新状态栏
        self.status_bar.showMessage(f"处理完成 | 成功: {success_count} | 失败: {failed_count}")
        self.progress_label.setText('处理完成')
        self.progress_percent_label.setText('100%')
        self._show_completion_feedback(success_count, failed_count)

        # 恢复按钮状态
        self.btn_start.setEnabled(len(self.video_files) > 0)
        self.btn_stop.setEnabled(False)
        self.chk_ai_enabled.setEnabled(True)
        self.combo_video_type.setEnabled(True)

        # 处理结果已经在workflow中写入数据库，这里不再重复写入

    def _save_to_history(self, results: list):
        """保存处理结果到历史记录"""
        self.logger.info("处理结果已由workflow持久化，跳过重复保存")

    def on_file_selected(self, current, previous):
        """文件选择变化"""
        if current:
            # 获取选中的文件索引
            index = self.file_list.row(current)
            if 0 <= index < len(self.video_files):
                video_file = self.video_files[index]

                info_text = f"""文件名: {video_file['name']}
大小: {video_file['size_mb']:.2f} MB ({video_file['size']:,} 字节)
路径: {video_file['path']}
格式: {video_file['extension']}
修改时间: {video_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.file_info_label.setText(info_text)

    def open_settings(self):
        """打开设置对话框"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_status_message("设置已更新")
            # 刷新配置显示
            is_enabled = self.config.get('subtitle.enabled', True) or self.config.get('speech.tts_enabled', False)
            self.chk_ai_enabled.setChecked(is_enabled)

    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>SmartCutElf - 智剪精灵</h2>
        <p>版本: 1.0.0</p>
        <p>一款基于AI的智能视频自动剪辑软件</p>
        <p>支持多种视频类型的高光片段自动检测与剪辑</p>
        """
        QMessageBox.about(self, '关于', about_text)

    def show_history(self):
        """显示历史记录"""
        from ui.history_dialog import HistoryDialog
        dialog = HistoryDialog(self)
        dialog.exec_()

    def add_status_message(self, message: str):
        """添加状态消息"""
        self.logger.info(message.strip())
        self.status_text.append(message.strip())

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self,
            '确认退出',
            '确定要退出 SmartCutElf 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 停止内存监控
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()

            # 停止处理线程
            if self.processing_thread and self.processing_thread.isRunning():
                self.workflow.stop_processing()
                self.processing_thread.wait()

            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        video_files = [f for f in files if Path(f).is_file()]

        if video_files:
            # 获取支持的扩展名
            supported_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
            files_to_add = [f for f in video_files if Path(f).suffix.lower() in supported_extensions]

            if files_to_add:
                # 添加到视频文件列表
                for file_path in files_to_add:
                    path = Path(file_path)
                    try:
                        stat = path.stat()
                        self.video_files.append({
                            'name': path.name,
                            'path': str(path),
                            'size': stat.st_size,
                            'size_mb': stat.st_size / (1024 * 1024),
                            'extension': path.suffix[1:].upper(),
                            'modified': datetime.fromtimestamp(stat.st_mtime)
                        })
                    except Exception as e:
                        self.logger.warning(f"无法读取文件 {path}: {e}")

                # 刷新文件列表显示
                self.file_list.clear()
                total_size = 0
                for i, video_file in enumerate(self.video_files, 1):
                    size_mb = video_file['size_mb']
                    total_size += size_mb
                    # 限制文件名长度，避免换行
                    name = video_file['name']
                    if len(name) > 30:
                        name = name[:27] + "..."
                    item_text = f"{i}. {name}\n   {size_mb:.1f} MB | {video_file['extension']}"
                    item = QListWidgetItem(item_text)
                    self.file_list.addItem(item)

                # 更新统计信息
                count = len(self.video_files)
                self.file_count_label.setText(f"{count} 个文件")

                stats = f"已添加 {len(files_to_add)} 个文件\n\n文件数量: {count}\n总大小: {total_size:.1f} MB\n平均大小: {total_size/count:.1f} MB"
                self.file_info_label.setText(stats)
                self.add_status_message(f"拖放添加了 {len(files_to_add)} 个视频文件")
                self.btn_start.setEnabled(True)
                self.file_stack.setCurrentWidget(self.file_list)
                self.status_banner.setText("素材已更新")
                self._set_stage("ready", "等待开始")
                self._fade_widget(self.file_list, 0.0, 1.0, 240)

                event.acceptProposedAction()

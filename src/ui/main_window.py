"""
主窗口
SmartCutElf的主用户界面
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QListWidget,
                             QProgressBar, QTextEdit, QSplitter, QMenuBar,
                             QMenu, QAction, QStatusBar, QMessageBox, QListWidgetItem,
                             QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont
from pathlib import Path
from utils.config import get_config
from utils.logger import setup_logger
from utils.file_manager import FileManager
from core.workflow import VideoProcessingWorkflow


class ProcessingThread(QThread):
    """视频处理线程"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(list)  # results
    
    def __init__(self, workflow, video_files):
        super().__init__()
        self.workflow = workflow
        self.video_files = video_files
    
    def run(self):
        """运行处理"""
        def progress_callback(current, total, message):
            self.progress.emit(current, total, message)
        
        results = self.workflow.process_batch(
            [f['path'] for f in self.video_files],
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
        
        self.video_files = []
        self.current_project_id = None
        self.processing_thread = None
        
        self._init_ui()
        self._apply_theme()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性 - 更大的默认尺寸
        self.setWindowTitle("SmartCutElf - 智剪精灵 v1.0")
        self.setGeometry(50, 50, 1400, 900)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部工具栏
        toolbar_layout = self._create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # 分割器（左侧文件列表，右侧预览区域）
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板  
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([350, 850])
        main_layout.addWidget(splitter)
        
        # 底部状态栏
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        open_folder_action = QAction('打开文件夹...', self)
        open_folder_action.setShortcut('Ctrl+O')
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        
        settings_action = QAction('设置...', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏"""
        toolbar = QHBoxLayout()
        
        # 打开文件夹按钮
        self.btn_open = QPushButton('📁 打开文件夹')
        self.btn_open.setMinimumHeight(45)
        self.btn_open.setMinimumWidth(150)
        self.btn_open.setFont(QFont('Microsoft YaHei', 10))
        self.btn_open.clicked.connect(self.open_folder)
        toolbar.addWidget(self.btn_open)
        
        # 开始处理按钮
        self.btn_start = QPushButton('▶️ 开始处理')
        self.btn_start.setMinimumHeight(45)
        self.btn_start.setMinimumWidth(150)
        self.btn_start.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_processing)
        toolbar.addWidget(self.btn_start)
        
        # 停止按钮
        self.btn_stop = QPushButton('⏹️ 停止')
        self.btn_stop.setMinimumHeight(45)
        self.btn_stop.setMinimumWidth(120)
        self.btn_stop.setFont(QFont('Microsoft YaHei', 10))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)
        toolbar.addWidget(self.btn_stop)
        
        toolbar.addStretch()
        
        # 字幕开关
        self.chk_subtitle = QCheckBox('生成字幕')
        self.chk_subtitle.setChecked(self.config.get('subtitle.enabled', True))
        self.chk_subtitle.setFont(QFont('Microsoft YaHei', 10))
        toolbar.addWidget(self.chk_subtitle)
        
        toolbar.addSpacing(20)
        
        # 设置按钮
        self.btn_settings = QPushButton('⚙️ 设置')
        self.btn_settings.setMinimumHeight(45)
        self.btn_settings.setMinimumWidth(120)
        self.btn_settings.setFont(QFont('Microsoft YaHei', 10))
        self.btn_settings.clicked.connect(self.open_settings)
        toolbar.addWidget(self.btn_settings)
        
        return toolbar
    
    def _create_left_panel(self) -> QWidget:
        """创建左侧文件列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题区域
        title_layout = QHBoxLayout()
        title = QLabel('📹 视频文件列表')
        title.setFont(QFont('Microsoft YaHei', 13, QFont.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # 文件数量标签
        self.file_count_label = QLabel('0 个文件')
        self.file_count_label.setFont(QFont('Microsoft YaHei', 10))
        title_layout.addWidget(self.file_count_label)
        
        layout.addLayout(title_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setFont(QFont('Microsoft YaHei', 9))
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        layout.addWidget(self.file_list)
        
        # 文件详细信息组
        info_group = QGroupBox('📊 文件信息')
        info_group.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
        info_layout = QVBoxLayout(info_group)
        
        self.file_info_label = QLabel('请选择文件夹以加载视频')
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setFont(QFont('Microsoft YaHei', 9))
        info_layout.addWidget(self.file_info_label)
        
        layout.addWidget(info_group)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """创建右侧预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题
        title = QLabel('📊 处理状态与进度')
        title.setFont(QFont('Microsoft YaHei', 13, QFont.Bold))
        layout.addWidget(title)
        
        # 进度信息
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel('等待开始...')
        self.progress_label.setFont(QFont('Microsoft YaHei', 10))
        progress_layout.addWidget(self.progress_label)
        progress_layout.addStretch()
        
        self.progress_percent_label = QLabel('0%')
        self.progress_percent_label.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
        progress_layout.addWidget(self.progress_percent_label)
        
        layout.addLayout(progress_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFont(QFont('Microsoft YaHei', 9))
        layout.addWidget(self.progress_bar)
        
        # 状态日志标题
        log_title = QLabel('📝 处理日志')
        log_title.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        layout.addWidget(log_title)
        
        # 状态文本
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText('准备就绪，等待开始处理...\n\n提示：\n1. 点击"打开文件夹"选择视频文件\n2. 点击"开始处理"进行自动剪辑\n3. 处理完成后在output文件夹查看结果')
        self.status_text.setFont(QFont('Consolas', 9))
        layout.addWidget(self.status_text)
        
        return panel
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')
    
    def _apply_theme(self):
        """应用主题样式"""
        theme = self.config.get('ui.theme', 'dark')
        
        if theme == 'dark':
            stylesheet = """
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1984d8;
                }
                QPushButton:pressed {
                    background-color: #006cbe;
                }
                QPushButton:disabled {
                    background-color: #3f3f3f;
                    color: #808080;
                }
                QListWidget {
                    background-color: #252526;
                    border: 1px solid #3f3f3f;
                    border-radius: 4px;
                }
                QTextEdit {
                    background-color: #252526;
                    border: 1px solid #3f3f3f;
                    border-radius: 4px;
                    font-family: 'Consolas', monospace;
                }
                QProgressBar {
                    border: 1px solid #3f3f3f;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #3f3f46;
                }
                QMenu {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f3f;
                }
                QMenu::item:selected {
                    background-color: #0078d4;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: white;
                }
            """
            self.setStyleSheet(stylesheet)
    
    def open_folder(self):
        """打开文件夹选择对话框"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择视频文件夹",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            self.load_videos(folder_path)
    
    def load_videos(self, folder_path: str):
        """加载视频文件"""
        self.logger.info(f"加载视频文件夹: {folder_path}")
        self.add_status_message(f"\n{'='*60}")
        self.add_status_message(f"🔍 正在扫描文件夹: {folder_path}")
        
        # 扫描视频文件
        self.video_files = self.file_manager.scan_video_files(folder_path)
        
        # 更新文件列表
        self.file_list.clear()
        total_size = 0
        for i, video_file in enumerate(self.video_files, 1):
            size_mb = video_file['size_mb']
            total_size += size_mb
            item_text = f"{i}. 📹 {video_file['name']}\n    大小: {size_mb:.1f} MB | 格式: {video_file['extension']}"
            item = QListWidgetItem(item_text)
            self.file_list.addItem(item)
        
        # 更新统计信息
        count = len(self.video_files)
        self.file_count_label.setText(f"{count} 个文件")
        
        if count > 0:
            stats = f"✅ 扫描完成！\n\n文件数量: {count}\n总大小: {total_size:.1f} MB\n平均大小: {total_size/count:.1f} MB"
            self.file_info_label.setText(stats)
            self.add_status_message(f"✅ 找到 {count} 个视频文件，总大小 {total_size:.1f} MB")
            self.status_bar.showMessage(f"已加载 {count} 个视频文件 | 总大小 {total_size:.1f} MB")
            self.btn_start.setEnabled(True)
        else:
            self.file_info_label.setText("❌ 未找到支持的视频文件")
            self.add_status_message("⚠️ 未找到支持的视频文件")
            self.status_bar.showMessage("未找到视频文件")
        
        self.add_status_message(f"{'='*60}\n")
    
    def start_processing(self):
        """开始处理视频"""
        if not self.video_files:
            QMessageBox.warning(self, '警告', '请先选择视频文件夹')
            return
        
        # 更新配置中的字幕设置
        self.config.set('subtitle.enabled', self.chk_subtitle.isChecked())
        self.config.save()
        
        self.logger.info("开始处理视频")
        self.add_status_message("\n" + "="*60)
        self.add_status_message("🎬 开始自动剪辑处理...")
        self.add_status_message(f"📁 待处理文件: {len(self.video_files)} 个")
        self.add_status_message(f"📝 字幕生成: {'✅ 启用' if self.chk_subtitle.isChecked() else '❌ 禁用'}")
        self.add_status_message("="*60 + "\n")
        
        # 禁用按钮
        self.btn_start.setEnabled(False)
        self.btn_open.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.chk_subtitle.setEnabled(False)
        
        # 重置进度
        self.progress_bar.setValue(0)
        self.progress_label.setText('正在处理...')
        self.progress_percent_label.setText('0%')
        
        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(self.workflow, self.video_files)
        self.processing_thread.progress.connect(self.on_processing_progress)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()
    
    def stop_processing(self):
        """停止处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self,
                '确认停止',
                '确定要停止处理吗？已处理的文件会保留。',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.logger.info("用户请求停止处理")
                self.add_status_message("\n⏹️ 正在停止处理...")
                self.workflow.stop_processing()
                self.processing_thread.wait()
        
        # 恢复按钮状态
        self.btn_start.setEnabled(len(self.video_files) > 0)
        self.btn_open.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.chk_subtitle.setEnabled(True)
    
    def on_processing_progress(self, current: int, total: int, message: str):
        """处理进度更新"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"{current}/{total} 个文件")
        self.progress_label.setText(f'处理中 ({current}/{total})')
        self.progress_percent_label.setText(f'{progress}%')
        
        self.add_status_message(f"[{current}/{total}] {message}")
        self.status_bar.showMessage(f"处理进度: {current}/{total} | {message}")
    
    def on_processing_finished(self, results: list):
        """处理完成"""
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = len(results) - success_count
        
        self.add_status_message("\n" + "="*60)
        self.add_status_message("✅ 批量处理完成！")
        self.add_status_message(f"📊 统计信息:")
        self.add_status_message(f"   • 成功: {success_count} 个")
        self.add_status_message(f"   • 失败: {failed_count} 个")
        self.add_status_message(f"   • 总计: {len(results)} 个")
        
        # 显示成功的文件
        if success_count > 0:
            self.add_status_message(f"\n✨ 成功处理的文件:")
            for i, result in enumerate([r for r in results if r.get('success')], 1):
                output_file = Path(result['output_path']).name
                duration = result.get('total_duration', 0)
                time_taken = result.get('processing_time', 0)
                self.add_status_message(f"   {i}. {output_file} | 时长: {duration:.1f}s | 耗时: {time_taken:.1f}s")
        
        # 显示失败的文件
        if failed_count > 0:
            self.add_status_message(f"\n❌ 处理失败的文件:")
            for i, result in enumerate([r for r in results if not r.get('success')], 1):
                input_file = Path(result.get('input_path', '未知文件')).name if result.get('input_path') else '未知文件'
                error = result.get('error', '未知错误')
                self.add_status_message(f"   {i}. {input_file} - {error}")
        
        self.add_status_message(f"\n💾 输出目录: {self.config.get('output.folder', 'output')}")
        self.add_status_message("="*60 + "\n")
        
        # 更新状态栏
        self.status_bar.showMessage(f"处理完成 | 成功: {success_count} | 失败: {failed_count}")
        self.progress_label.setText('处理完成')
        self.progress_percent_label.setText('100%')
        
        # 恢复按钮状态
        self.btn_start.setEnabled(True)
        self.btn_open.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.chk_subtitle.setEnabled(True)
        
        # 显示完成消息框
        if success_count > 0:
            QMessageBox.information(
                self,
                '处理完成',
                f'成功处理 {success_count} 个视频文件！\n\n输出目录: {self.config.get("output.folder", "output")}'
            )
        else:
            QMessageBox.warning(
                self,
                '处理失败',
                f'所有文件处理失败，请检查日志了解详情。'
            )
    
    def on_file_selected(self, current, previous):
        """文件选择改变"""
        if current:
            # 获取选中的文件索引
            index = self.file_list.row(current)
            if 0 <= index < len(self.video_files):
                video_file = self.video_files[index]
                
                info_text = f"""📹 文件名: {video_file['name']}
📏 大小: {video_file['size_mb']:.2f} MB ({video_file['size']:,} 字节)
📁 路径: {video_file['path']}
🎞️ 格式: {video_file['extension']}
📅 修改时间: {video_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.file_info_label.setText(info_text)
    
    def open_settings(self):
        """打开设置对话框"""
        # TODO: 实现设置对话框
        QMessageBox.information(self, '提示', '设置功能正在开发中...')
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>SmartCutElf - 智剪精灵</h2>
        <p>版本: 1.0.0</p>
        <p>一款基于AI的智能视频自动剪辑软件</p>
        <p><b>功能特点：</b></p>
        <ul>
            <li>智能识别精彩片段</li>
            <li>自动生成字幕</li>
            <li>视频自动剪辑</li>
            <li>语音识别和合成</li>
        </ul>
        <p>© 2024 SmartCutElf Team</p>
        """
        QMessageBox.about(self, '关于 SmartCutElf', about_text)
    
    def add_status_message(self, message: str):
        """添加状态消息"""
        self.status_text.append(message)
        # 滚动到底部
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
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
            self.logger.info("应用程序关闭")
            event.accept()
        else:
            event.ignore()

"""
处理历史查看对话框
显示所有视频处理记录
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QWidget, QLabel, QMessageBox,
                             QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pathlib import Path
from datetime import datetime
from utils.database import get_database


class HistoryDialog(QDialog):
    """处理历史对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("处理历史")
        self.setMinimumSize(900, 600)
        self.setObjectName("SettingsShell")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("历史记录与项目归档")
        title.setObjectName("HeroTitle")
        layout.addWidget(title)

        subtitle = QLabel("查看最近处理结果、统计耗时，并按批次管理历史项目。")
        subtitle.setObjectName("HeroSubtitle")
        layout.addWidget(subtitle)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 处理记录页
        self._create_records_tab()

        # 项目管理页
        self._create_projects_tab()

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self._load_data)
        button_layout.addWidget(refresh_btn)

        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_records_tab(self):
        """创建处理记录页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 统计信息
        stats_label = QLabel('处理统计')
        stats_label.setObjectName("SectionTitle")
        layout.addWidget(stats_label)

        self.stats_info = QLabel()
        self.stats_info.setObjectName("StatsCard")
        self.stats_info.setContentsMargins(14, 14, 14, 14)
        self.stats_info.setMargin(14)
        layout.addWidget(self.stats_info)

        # 表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels([
            '文件名', '输出路径', '处理时间', '视频时长', '处理日期', '项目'
        ])

        # 设置表格属性
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.setColumnWidth(0, 200)
        self.records_table.setColumnWidth(1, 250)
        self.records_table.setColumnWidth(2, 100)
        self.records_table.setColumnWidth(3, 100)
        self.records_table.setColumnWidth(4, 150)

        layout.addWidget(self.records_table)

        self.tab_widget.addTab(tab, '📋 处理记录')

    def _create_projects_tab(self):
        """创建项目管理页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 项目表格
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels([
            '项目名称', '文件数量', '完成数量', '创建时间', '操作'
        ])

        # 设置表格属性
        self.projects_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.projects_table.horizontalHeader().setStretchLastSection(True)
        self.projects_table.setColumnWidth(0, 200)
        self.projects_table.setColumnWidth(1, 100)
        self.projects_table.setColumnWidth(2, 100)
        self.projects_table.setColumnWidth(3, 180)

        layout.addWidget(self.projects_table)

        self.tab_widget.addTab(tab, '📦 项目管理')

    def _load_data(self):
        """加载数据"""
        # 加载处理记录
        records = self.db.get_all_processing_history(limit=200)

        self.records_table.setRowCount(len(records))

        total_time = 0
        total_duration = 0

        for row, record in enumerate(records):
            # 文件名
            self.records_table.setItem(row, 0, QTableWidgetItem(record.get('file_name', 'N/A')))

            # 输出路径
            output_path = record.get('output_path', '')
            self.records_table.setItem(row, 1, QTableWidgetItem(output_path))

            # 处理时间
            proc_time = record.get('processing_time', 0)
            self.records_table.setItem(row, 2, QTableWidgetItem(f"{proc_time:.1f}s"))
            total_time += proc_time

            # 视频时长
            duration = record.get('duration', 0)
            self.records_table.setItem(row, 3, QTableWidgetItem(f"{duration:.1f}s"))
            total_duration += duration

            # 处理日期
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('T', ' ').split('.')[0])
                    created_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    created_str = created_at
            else:
                created_str = 'N/A'
            self.records_table.setItem(row, 4, QTableWidgetItem(created_str))

            # 项目名称
            project_name = record.get('project_name', 'N/A')
            self.records_table.setItem(row, 5, QTableWidgetItem(project_name))

        # 更新统计信息
        avg_time = total_time / len(records) if records else 0
        stats_text = f"📊 总记录数: {len(records)} | 总处理时间: {total_time:.1f}s | 平均处理时间: {avg_time:.1f}s | 总视频时长: {total_duration:.1f}s"
        self.stats_info.setText(stats_text)

        # 加载项目列表
        projects = self.db.get_all_projects()

        self.projects_table.setRowCount(len(projects))

        for row, project in enumerate(projects):
            # 项目名称
            self.projects_table.setItem(row, 0, QTableWidgetItem(project.get('name', 'N/A')))

            # 文件数量
            file_count = project.get('file_count', 0)
            self.projects_table.setItem(row, 1, QTableWidgetItem(str(file_count)))

            # 完成数量
            completed_count = project.get('completed_count', 0)
            self.projects_table.setItem(row, 2, QTableWidgetItem(str(completed_count)))

            # 创建时间
            created_at = project.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('T', ' ').split('.')[0])
                    created_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    created_str = created_at
            else:
                created_str = 'N/A'
            self.projects_table.setItem(row, 3, QTableWidgetItem(created_str))

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            delete_btn = QPushButton('删除')
            delete_btn.setProperty("secondary", True)
            delete_btn.clicked.connect(lambda checked, pid=project.get('id'): self._delete_project(pid))
            btn_layout.addWidget(delete_btn)

            btn_layout.addStretch()
            self.projects_table.setCellWidget(row, 4, btn_widget)

    def _delete_project(self, project_id: int):
        """删除项目"""
        reply = QMessageBox.question(
            self,
            '确认删除',
            '确定要删除此项目及其所有相关数据吗？此操作不可撤销。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_project(project_id)
                self._load_data()
                QMessageBox.information(self, '成功', '项目已删除')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除失败: {e}')

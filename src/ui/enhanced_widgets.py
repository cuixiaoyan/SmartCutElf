"""
增强的UI组件
包括快捷操作、空状态等
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush


class EmptyStateIllustration(QWidget):
    """克制的几何占位图形"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(108, 84)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        card = QRectF(rect.left() + 16, rect.top() + 14, rect.width() - 32, rect.height() - 20)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(239, 243, 248, 255)))
        painter.drawRoundedRect(card, 18, 18)

        painter.setBrush(QBrush(QColor(22, 119, 255, 34)))
        painter.drawEllipse(QRectF(rect.left() + 10, rect.top() + 8, 24, 24))

        painter.setPen(QPen(QColor(22, 119, 255, 95), 1.5))
        painter.setBrush(QBrush(QColor(22, 119, 255, 22)))
        painter.drawRoundedRect(QRectF(card.left() + 14, card.top() + 14, card.width() - 28, 14), 7, 7)
        painter.drawRoundedRect(QRectF(card.left() + 14, card.top() + 36, card.width() - 42, 8), 4, 4)
        painter.drawRoundedRect(QRectF(card.left() + 14, card.top() + 50, card.width() - 56, 8), 4, 4)

        painter.setBrush(QBrush(QColor(22, 119, 255, 110)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(card.right() - 24, card.top() + 12, 8, 8))

        painter.end()


class GuidedEmptyState(QWidget):
    """带插画的引导空状态"""

    def __init__(self, title_text: str, body_text: str, button_text: str, callback, parent=None):
        super().__init__(parent)
        self._init_ui(title_text, body_text, button_text, callback)

    def _init_ui(self, title_text: str, body_text: str, button_text: str, callback):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        illustration = EmptyStateIllustration()
        layout.addWidget(illustration, 0, Qt.AlignCenter)

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        body = QLabel(body_text)
        body.setObjectName("SectionCaption")
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        layout.addWidget(body)

        action = QPushButton(button_text)
        action.setProperty("primary", True)
        action.setFixedSize(112, 34)
        action.clicked.connect(callback)
        layout.addWidget(action, 0, Qt.AlignCenter)


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
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        # 统一按钮尺寸
        btn_h = 36

        # 打开输出目录
        self.btn_open_output = QPushButton('查看成片')
        self.btn_open_output.setFixedHeight(btn_h)
        self.btn_open_output.setMinimumWidth(112)
        self.btn_open_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_open_output.clicked.connect(self.open_output_clicked.emit)
        layout.addWidget(self.btn_open_output)

        # 复制日志
        self.btn_copy_log = QPushButton('复制日志')
        self.btn_copy_log.setFixedHeight(btn_h)
        self.btn_copy_log.setMinimumWidth(112)
        self.btn_copy_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_copy_log.clicked.connect(self.copy_log_clicked.emit)
        layout.addWidget(self.btn_copy_log)

        # 导出日志
        self.btn_export_log = QPushButton('导出记录')
        self.btn_export_log.setFixedHeight(btn_h)
        self.btn_export_log.setMinimumWidth(112)
        self.btn_export_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_export_log.clicked.connect(self.export_log_clicked.emit)
        layout.addWidget(self.btn_export_log)

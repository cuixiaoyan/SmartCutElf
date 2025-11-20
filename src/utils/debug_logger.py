"""
增强的日志系统
支持用户模式和调试模式
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogMode(Enum):
    """日志模式"""
    USER = "user"  # 用户模式：简洁友好
    DEBUG = "debug"  # 调试模式：详细技术信息


class EnhancedLogger:
    """增强的日志器"""
    
    def __init__(self, name: str, mode: LogMode = LogMode.USER, log_dir: str = "logs"):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            mode: 日志模式
            log_dir: 日志目录
        """
        self.name = name
        self.mode = mode
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if mode == LogMode.DEBUG else logging.INFO)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加处理器
        self._setup_handlers()
        
        # 用户友好消息缓存
        self.user_messages = []
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 文件处理器 - 详细日志
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        if self.mode == LogMode.DEBUG:
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(message)s')
        
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _format_user_message(self, level: str, message: str) -> str:
        """格式化用户友好消息"""
        icons = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }
        
        icon = icons.get(level, "•")
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if self.mode == LogMode.DEBUG:
            return f"[{timestamp}] {icon} {message}"
        else:
            return f"{icon} {message}"
    
    def debug(self, message: str, technical_detail: str = ""):
        """调试日志"""
        if self.mode == LogMode.DEBUG:
            full_message = f"{message} | {technical_detail}" if technical_detail else message
            self.logger.debug(full_message)
        else:
            self.logger.debug(message)
    
    def info(self, message: str, user_message: Optional[str] = None):
        """信息日志"""
        self.logger.info(message)
        
        # 用户友好消息
        display_message = user_message or message
        formatted = self._format_user_message("INFO", display_message)
        self.user_messages.append(formatted)
    
    def warning(self, message: str, user_message: Optional[str] = None):
        """警告日志"""
        self.logger.warning(message)
        
        display_message = user_message or message
        formatted = self._format_user_message("WARNING", display_message)
        self.user_messages.append(formatted)
    
    def error(self, message: str, user_message: Optional[str] = None, exception: Exception = None):
        """错误日志"""
        if exception and self.mode == LogMode.DEBUG:
            self.logger.error(f"{message}", exc_info=True)
        else:
            self.logger.error(message)
        
        display_message = user_message or message
        formatted = self._format_user_message("ERROR", display_message)
        self.user_messages.append(formatted)
    
    def critical(self, message: str, user_message: Optional[str] = None):
        """严重错误日志"""
        self.logger.critical(message)
        
        display_message = user_message or message
        formatted = self._format_user_message("CRITICAL", display_message)
        self.user_messages.append(formatted)
    
    def progress(self, current: int, total: int, message: str = ""):
        """进度日志"""
        percent = (current / total * 100) if total > 0 else 0
        progress_bar = self._create_progress_bar(percent)
        
        if self.mode == LogMode.DEBUG:
            log_message = f"进度: {current}/{total} ({percent:.1f}%) {message}"
        else:
            log_message = f"{progress_bar} {percent:.0f}% {message}"
        
        formatted = self._format_user_message("INFO", log_message)
        self.user_messages.append(formatted)
        self.logger.info(log_message)
    
    def _create_progress_bar(self, percent: float, width: int = 20) -> str:
        """创建进度条"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def section(self, title: str):
        """章节分隔"""
        separator = "=" * 60
        formatted = f"\n{separator}\n{title}\n{separator}"
        self.user_messages.append(formatted)
        self.logger.info(formatted)
    
    def get_user_messages(self) -> list:
        """获取用户友好消息列表"""
        return self.user_messages.copy()
    
    def clear_user_messages(self):
        """清空用户消息"""
        self.user_messages.clear()
    
    def export_log(self, export_path: Optional[str] = None) -> str:
        """
        导出日志
        
        Returns:
            导出的文件路径
        """
        if export_path is None:
            export_path = self.log_dir / f"{self.name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        export_path = Path(export_path)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(f"SmartCutElf 日志导出\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"日志模式: {self.mode.value}\n")
            f.write("=" * 60 + "\n\n")
            
            for message in self.user_messages:
                f.write(message + "\n")
        
        return str(export_path)


class DebugHelper:
    """调试辅助工具"""
    
    @staticmethod
    def format_dict(data: dict, indent: int = 2) -> str:
        """格式化字典为可读文本"""
        import json
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def format_exception(exception: Exception) -> str:
        """格式化异常信息"""
        import traceback
        return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    @staticmethod
    def get_system_info() -> dict:
        """获取系统信息"""
        import platform
        import psutil
        
        return {
            "系统": platform.system(),
            "版本": platform.version(),
            "架构": platform.machine(),
            "Python版本": platform.python_version(),
            "CPU核心数": psutil.cpu_count(),
            "内存总量": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "可用内存": f"{psutil.virtual_memory().available / (1024**3):.2f} GB"
        }
    
    @staticmethod
    def create_debug_report(logger: EnhancedLogger, error: Exception = None) -> str:
        """创建调试报告"""
        report = []
        report.append("=" * 60)
        report.append("SmartCutElf 调试报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 系统信息
        report.append("## 系统信息")
        system_info = DebugHelper.get_system_info()
        for key, value in system_info.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        # 错误信息
        if error:
            report.append("## 错误信息")
            report.append(f"  类型: {type(error).__name__}")
            report.append(f"  消息: {str(error)}")
            report.append("")
            report.append("## 堆栈跟踪")
            report.append(DebugHelper.format_exception(error))
            report.append("")
        
        # 日志
        report.append("## 日志记录")
        for message in logger.get_user_messages():
            report.append(message)
        
        return "\n".join(report)


# 全局日志器实例
_global_logger: Optional[EnhancedLogger] = None


def get_enhanced_logger(name: str = "SmartCutElf", mode: LogMode = LogMode.USER) -> EnhancedLogger:
    """获取全局日志器"""
    global _global_logger
    if _global_logger is None:
        _global_logger = EnhancedLogger(name, mode)
    return _global_logger


def set_log_mode(mode: LogMode):
    """设置日志模式"""
    global _global_logger
    if _global_logger:
        _global_logger.mode = mode
        _global_logger._setup_handlers()

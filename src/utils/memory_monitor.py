"""
内存监控工具
实时监控应用程序内存使用情况
"""

import psutil
from typing import Dict
from utils.logger import LoggerMixin


class MemoryMonitor(LoggerMixin):
    """内存监控器"""
    
    def __init__(self):
        """初始化内存监控器"""
        super().__init__()
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        获取当前内存使用情况
        
        Returns:
            内存使用信息字典
        """
        try:
            mem_info = self.process.memory_info()
            
            return {
                'rss_mb': mem_info.rss / (1024 * 1024),  # 实际物理内存
                'vms_mb': mem_info.vms / (1024 * 1024),  # 虚拟内存
                'percent': self.process.memory_percent(),  # 占系统总内存百分比
            }
        except Exception as e:
            self.logger.error(f"获取内存信息失败: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
    
    def get_memory_str(self) -> str:
        """
        获取内存使用的字符串表示
        
        Returns:
            格式化的内存字符串，如 "256.5MB (2.5%)"
        """
        mem = self.get_memory_usage()
        return f"{mem['rss_mb']:.1f}MB ({mem['percent']:.1f}%)"
    
    def get_system_memory(self) -> Dict[str, float]:
        """
        获取系统整体内存情况
        
        Returns:
            系统内存信息
        """
        try:
            sys_mem = psutil.virtual_memory()
            
            return {
                'total_gb': sys_mem.total / (1024 * 1024 * 1024),
                'available_gb': sys_mem.available / (1024 * 1024 * 1024),
                'used_gb': sys_mem.used / (1024 * 1024 * 1024),
                'percent': sys_mem.percent
            }
        except Exception as e:
            self.logger.error(f"获取系统内存信息失败: {e}")
            return {'total_gb': 0, 'available_gb': 0, 'used_gb': 0, 'percent': 0}
    
    def check_memory_threshold(self, threshold_mb: float = 1000) -> bool:
        """
        检查内存使用是否超过阈值
        
        Args:
            threshold_mb: 阈值（MB）
            
        Returns:
            是否超过阈值
        """
        mem = self.get_memory_usage()
        if mem['rss_mb'] > threshold_mb:
            self.logger.warning(
                f"内存使用过高: {mem['rss_mb']:.1f}MB > {threshold_mb}MB"
            )
            return True
        return False
    
    def log_memory_status(self):
        """记录当前内存状态到日志"""
        mem = self.get_memory_usage()
        sys_mem = self.get_system_memory()
        
        self.logger.info(
            f"内存状态 - 进程: {mem['rss_mb']:.1f}MB ({mem['percent']:.1f}%) | "
            f"系统: {sys_mem['used_gb']:.1f}/{sys_mem['total_gb']:.1f}GB "
            f"({sys_mem['percent']:.1f}%)"
        )


# 全局单例
_global_monitor = None


def get_memory_monitor() -> MemoryMonitor:
    """获取全局内存监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MemoryMonitor()
    return _global_monitor

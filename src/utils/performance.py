"""
性能监控和优化
包括内存监控、进度管理、断点续传
"""

import psutil
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ProcessingProgress:
    """处理进度数据"""
    video_path: str
    total_duration: float
    processed_duration: float
    start_time: float
    current_step: str
    step_progress: float  # 0-1
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def get_progress_percent(self) -> float:
        """获取总体进度百分比"""
        if self.total_duration == 0:
            return 0
        return (self.processed_duration / self.total_duration) * 100


class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, warning_threshold: float = 80.0, critical_threshold: float = 90.0):
        """
        初始化内存监控器
        
        Args:
            warning_threshold: 警告阈值（百分比）
            critical_threshold: 危险阈值（百分比）
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> Dict:
        """获取内存使用情况"""
        # 系统内存
        system_memory = psutil.virtual_memory()
        
        # 进程内存
        process_memory = self.process.memory_info()
        
        return {
            'system': {
                'total': system_memory.total,
                'available': system_memory.available,
                'used': system_memory.used,
                'percent': system_memory.percent
            },
            'process': {
                'rss': process_memory.rss,  # 实际物理内存
                'vms': process_memory.vms,  # 虚拟内存
                'percent': self.process.memory_percent()
            }
        }
    
    def check_memory_status(self) -> tuple[str, str]:
        """
        检查内存状态
        
        Returns:
            (status, message) - status: 'ok', 'warning', 'critical'
        """
        memory = self.get_memory_usage()
        percent = memory['system']['percent']
        
        if percent >= self.critical_threshold:
            return 'critical', f'内存使用率过高: {percent:.1f}%，建议关闭其他程序'
        elif percent >= self.warning_threshold:
            return 'warning', f'内存使用率较高: {percent:.1f}%，注意监控'
        else:
            return 'ok', f'内存使用正常: {percent:.1f}%'
    
    def format_size(self, bytes_size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def get_memory_info_text(self) -> str:
        """获取内存信息文本"""
        memory = self.get_memory_usage()
        
        text = "💾 内存使用情况:\n"
        text += f"  系统: {self.format_size(memory['system']['used'])} / "
        text += f"{self.format_size(memory['system']['total'])} "
        text += f"({memory['system']['percent']:.1f}%)\n"
        text += f"  本程序: {self.format_size(memory['process']['rss'])} "
        text += f"({memory['process']['percent']:.1f}%)"
        
        return text


class ProgressManager:
    """进度管理器 - 支持断点续传"""
    
    def __init__(self, cache_dir: str = "cache/progress"):
        """初始化进度管理器"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.current_progress: Dict[str, ProcessingProgress] = {}
    
    def _get_cache_file(self, video_path: str) -> Path:
        """获取缓存文件路径"""
        # 使用文件路径的哈希作为缓存文件名
        import hashlib
        file_hash = hashlib.md5(video_path.encode()).hexdigest()
        return self.cache_dir / f"{file_hash}.json"
    
    def save_progress(self, video_path: str, progress: ProcessingProgress):
        """保存进度"""
        cache_file = self._get_cache_file(video_path)
        self.current_progress[video_path] = progress
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(progress.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进度失败: {e}")
    
    def load_progress(self, video_path: str) -> Optional[ProcessingProgress]:
        """加载进度"""
        cache_file = self._get_cache_file(video_path)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                progress = ProcessingProgress.from_dict(data)
                self.current_progress[video_path] = progress
                return progress
        except Exception as e:
            print(f"加载进度失败: {e}")
            return None
    
    def clear_progress(self, video_path: str):
        """清除进度"""
        cache_file = self._get_cache_file(video_path)
        
        if cache_file.exists():
            cache_file.unlink()
        
        if video_path in self.current_progress:
            del self.current_progress[video_path]
    
    def get_progress(self, video_path: str) -> Optional[ProcessingProgress]:
        """获取当前进度"""
        return self.current_progress.get(video_path)
    
    def has_progress(self, video_path: str) -> bool:
        """检查是否有保存的进度"""
        return self._get_cache_file(video_path).exists()


class PerformanceEstimator:
    """性能预估器"""
    
    def __init__(self, history_file: str = "cache/performance_history.json"):
        """初始化性能预估器"""
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """加载历史数据"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self):
        """保存历史数据"""
        try:
            # 只保留最近100条记录
            history_to_save = self.history[-100:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史数据失败: {e}")
    
    def record_processing(self, file_size_mb: float, duration_sec: float, 
                         processing_time_sec: float, success: bool):
        """记录处理数据"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'file_size_mb': file_size_mb,
            'duration_sec': duration_sec,
            'processing_time_sec': processing_time_sec,
            'success': success,
            'speed_ratio': duration_sec / processing_time_sec if processing_time_sec > 0 else 0
        }
        
        self.history.append(record)
        self._save_history()
    
    def estimate_time(self, file_size_mb: float, duration_sec: float) -> float:
        """
        预估处理时间
        
        Returns:
            预估时间（秒）
        """
        if not self.history:
            # 没有历史数据，使用默认估算
            # 假设处理速度为实时的 0.5 倍（即处理10秒视频需要20秒）
            return duration_sec * 2.0
        
        # 使用最近的成功记录计算平均速度
        recent_success = [h for h in self.history[-20:] if h['success']]
        
        if not recent_success:
            return duration_sec * 2.0
        
        # 计算平均处理速度比
        avg_speed_ratio = sum(h['speed_ratio'] for h in recent_success) / len(recent_success)
        
        if avg_speed_ratio == 0:
            return duration_sec * 2.0
        
        # 预估时间 = 视频时长 / 速度比
        estimated = duration_sec / avg_speed_ratio
        
        # 添加10%的缓冲
        return estimated * 1.1
    
    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
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


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.memory_monitor = MemoryMonitor()
    
    def get_optimal_workers(self, file_count: int, max_workers: int = 4) -> int:
        """
        根据系统资源获取最优工作线程数
        
        Args:
            file_count: 待处理文件数
            max_workers: 最大工作线程数
            
        Returns:
            推荐的工作线程数
        """
        # 获取CPU核心数
        cpu_count = psutil.cpu_count(logical=False) or 2
        
        # 获取内存使用情况
        memory = self.memory_monitor.get_memory_usage()
        memory_percent = memory['system']['percent']
        
        # 根据内存使用情况调整
        if memory_percent > 80:
            # 内存紧张，减少并行数
            optimal = max(1, cpu_count // 2)
        elif memory_percent > 60:
            # 内存一般，使用中等并行数
            optimal = cpu_count
        else:
            # 内存充足，可以使用更多并行
            optimal = min(cpu_count + 2, max_workers)
        
        # 不超过文件数量
        optimal = min(optimal, file_count)
        
        # 不超过配置的最大值
        optimal = min(optimal, max_workers)
        
        return max(1, optimal)
    
    def should_pause_processing(self) -> tuple[bool, str]:
        """
        检查是否应该暂停处理
        
        Returns:
            (should_pause, reason)
        """
        status, message = self.memory_monitor.check_memory_status()
        
        if status == 'critical':
            return True, message
        
        return False, ""

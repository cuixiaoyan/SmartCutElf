"""
FFmpeg进程池
用于并行处理多个视频任务，提升性能
"""

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Callable, List, Any, Dict
import functools
from utils.logger import LoggerMixin


class FFmpegPool(LoggerMixin):
    """FFmpeg任务进程池"""
    
    def __init__(self, max_workers: int = 2, use_processes: bool = False):
        """
        初始化FFmpeg进程池
        
        Args:
            max_workers: 最大并行数（建议2-4，避免CPU过载）
            use_processes: 是否使用进程池（True）还是线程池（False）
        """
        super().__init__()
        self.max_workers = max_workers
        
        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
            self.logger.info(f"使用进程池，最大并行数: {max_workers}")
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.logger.info(f"使用线程池，最大并行数: {max_workers}")
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """
        提交单个任务
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future对象
        """
        return self.executor.submit(func, *args, **kwargs)
    
    def submit_batch(self, func: Callable, args_list: List[tuple]) -> List:
        """
        批量提交任务并等待完成
        
        Args:
            func: 要执行的函数
            args_list: 参数列表，每个元素是一个元组
            
        Returns:
            结果列表
        """
        futures = [self.executor.submit(func, *args) for args in args_list]
        results = []
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"任务执行失败: {e}")
                results.append(None)
        
        return results
    
    def map_tasks(self, func: Callable, items: List[Any], 
                   progress_callback=None) -> List:
        """
        映射任务到多个项目
        
        Args:
            func: 要执行的函数
            items: 要处理的项目列表
            progress_callback: 进度回调 callback(current, total)
            
        Returns:
            结果列表
        """
        futures = {self.executor.submit(func, item): i 
                   for i, item in enumerate(items)}
        
        results = [None] * len(items)
        completed = 0
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(items))
                    
            except Exception as e:
                self.logger.error(f"任务 {idx} 失败: {e}")
                results[idx] = None
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(items))
        
        return results
    
    def shutdown(self, wait: bool = True):
        """
        关闭进程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)
        self.logger.info("FFmpeg进程池已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()


# 全局单例
_global_pool = None


def get_ffmpeg_pool(max_workers: int = 2) -> FFmpegPool:
    """
    获取全局FFmpeg进程池单例
    
    Args:
        max_workers: 最大并行数
        
    Returns:
        FFmpegPool实例
    """
    global _global_pool
    if _global_pool is None:
        _global_pool = FFmpegPool(max_workers=max_workers)
    return _global_pool

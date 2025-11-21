"""
智能文件等待工具
优化替代固定time.sleep延迟
"""

import os
import time
from pathlib import Path
from typing import Optional


def wait_for_file(
    filepath: str, 
    timeout: int = 10,
    min_size: int = 0
) -> bool:
    """
    智能等待文件完全写入
    
    Args:
        filepath: 文件路径
        timeout: 超时时间（秒）
        min_size: 最小文件大小（字节），0表示不检查
        
    Returns:
        文件是否可用
    """
    file_path = Path(filepath)
    start_time = time.time()
    last_size = -1
    
    while time.time() - start_time < timeout:
        if not file_path.exists():
            time.sleep(0.1)
            continue
        
        try:
            current_size = file_path.stat().st_size
            
            # 检查最小大小
            if min_size > 0 and current_size < min_size:
                time.sleep(0.1)
                continue
            
            # 检查文件大小是否稳定（不再增长）
            if current_size == last_size and current_size > 0:
                # 文件大小稳定，说明写入完成
                return True
            
            last_size = current_size
            time.sleep(0.1)
            
        except (OSError, IOError):
            time.sleep(0.1)
            continue
    
    return False


def wait_for_files(
    filepaths: list, 
    timeout: int = 30
) -> tuple:
    """
    等待多个文件完成
    
    Args:
        filepaths: 文件路径列表
        timeout: 总超时时间
        
    Returns:
        (成功的文件列表, 失败的文件列表)
    """
    success = []
    failed = []
    per_file_timeout = timeout / max(len(filepaths), 1)
    
    for filepath in filepaths:
        if wait_for_file(filepath, timeout=int(per_file_timeout)):
            success.append(filepath)
        else:
            failed.append(filepath)
    
    return success, failed


def verify_file_complete(filepath: str, stable_duration: float = 0.5) -> bool:
    """
    验证文件写入完成（大小稳定一段时间）
    
    Args:
        filepath: 文件路径
        stable_duration: 稳定持续时间（秒）
        
    Returns:
        文件是否完整
    """
    file_path = Path(filepath)
    
    if not file_path.exists():
        return False
    
    try:
        initial_size = file_path.stat().st_size
        time.sleep(stable_duration)
        final_size = file_path.stat().st_size
        
        # 大小未变化且不为0
        return initial_size == final_size and final_size > 0
    except (OSError, IOError):
        return False

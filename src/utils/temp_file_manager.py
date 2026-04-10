"""
临时文件管理
管理和清理临时文件
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from utils.logger import LoggerMixin


class TempFileManager(LoggerMixin):
    """临时文件管理器"""
    
    def __init__(self, app_name: str = "SmartCutElf"):
        """
        初始化临时文件管理器
        
        Args:
            app_name: 应用名称，用于创建临时目录
        """
        super().__init__()
        self.app_name = app_name
        self.temp_root = Path(tempfile.gettempdir()) / app_name
        self.temp_root.mkdir(parents=True, exist_ok=True)
    
    def get_temp_dir(self, subdir: str = "") -> Path:
        """
        获取临时目录
        
        Args:
            subdir: 子目录名称
            
        Returns:
            临时目录路径
        """
        if subdir:
            temp_dir = self.temp_root / subdir
        else:
            temp_dir = self.temp_root
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def get_temp_file(self, filename: str, subdir: str = "") -> Path:
        """
        获取临时文件路径
        
        Args:
            filename: 文件名
            subdir: 子目录名称
            
        Returns:
            临时文件路径
        """
        temp_dir = self.get_temp_dir(subdir)
        return temp_dir / filename
    
    def create_unique_temp_file(self, prefix: str = "", suffix: str = "", 
                               subdir: str = "") -> Path:
        """
        创建唯一的临时文件
        
        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀
            subdir: 子目录名称
            
        Returns:
            临时文件路径
        """
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{prefix}{unique_id}{suffix}"
        return self.get_temp_file(filename, subdir)
    
    def clean_temp_files(self, subdir: str = "", 
                        older_than_hours: Optional[int] = None):
        """
        清理临时文件
        
        Args:
            subdir: 子目录名称，为空则清理所有
            older_than_hours: 只清理超过指定小时数的文件，None 则清理所有
        """
        if subdir:
            target_dir = self.temp_root / subdir
        else:
            target_dir = self.temp_root
        
        if not target_dir.exists():
            return
        
        cleaned_count = 0
        cleaned_size = 0
        
        try:
            # 如果指定了时间限制
            if older_than_hours is not None:
                cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
                
                for item in target_dir.rglob('*'):
                    if item.is_file():
                        # 检查文件修改时间
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime < cutoff_time:
                            try:
                                file_size = item.stat().st_size
                                item.unlink()
                                cleaned_count += 1
                                cleaned_size += file_size
                            except Exception as e:
                                self.logger.warning(f"删除文件失败 {item}: {e}")
            else:
                # 清理所有文件
                if subdir:
                    # 清理指定子目录
                    for item in target_dir.iterdir():
                        try:
                            if item.is_file():
                                file_size = item.stat().st_size
                                item.unlink()
                                cleaned_count += 1
                                cleaned_size += file_size
                            elif item.is_dir():
                                dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                shutil.rmtree(item)
                                cleaned_count += 1
                                cleaned_size += dir_size
                        except Exception as e:
                            self.logger.warning(f"删除失败 {item}: {e}")
                else:
                    # 清理整个临时目录（保留目录结构）
                    for subdir_item in target_dir.iterdir():
                        if subdir_item.is_dir():
                            try:
                                dir_size = sum(f.stat().st_size for f in subdir_item.rglob('*') if f.is_file())
                                shutil.rmtree(subdir_item)
                                cleaned_count += 1
                                cleaned_size += dir_size
                            except Exception as e:
                                self.logger.warning(f"删除目录失败 {subdir_item}: {e}")
            
            if cleaned_count > 0:
                size_mb = cleaned_size / (1024 * 1024)
                self.logger.info(f"清理完成: {cleaned_count} 项, {size_mb:.2f} MB")
        
        except Exception as e:
            self.logger.error(f"清理临时文件时出错: {e}")
    
    def get_temp_size(self, subdir: str = "") -> tuple[int, int]:
        """
        获取临时文件占用空间
        
        Args:
            subdir: 子目录名称
            
        Returns:
            (文件数量, 总大小字节)
        """
        if subdir:
            target_dir = self.temp_root / subdir
        else:
            target_dir = self.temp_root
        
        if not target_dir.exists():
            return 0, 0
        
        file_count = 0
        total_size = 0
        
        for item in target_dir.rglob('*'):
            if item.is_file():
                file_count += 1
                try:
                    total_size += item.stat().st_size
                except:
                    pass
        
        return file_count, total_size
    
    def format_size(self, bytes_size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def get_temp_info(self) -> str:
        """获取临时文件信息"""
        file_count, total_size = self.get_temp_size()
        
        info = f"📁 临时文件目录: {self.temp_root}\n"
        info += f"📊 文件数量: {file_count}\n"
        info += f"💾 占用空间: {self.format_size(total_size)}\n"
        
        # 各子目录信息
        subdirs = [d for d in self.temp_root.iterdir() if d.is_dir()]
        if subdirs:
            info += "\n子目录:\n"
            for subdir in subdirs:
                count, size = self.get_temp_size(subdir.name)
                info += f"  • {subdir.name}: {count} 文件, {self.format_size(size)}\n"
        
        return info


# 全局实例
_temp_manager: Optional[TempFileManager] = None


def get_temp_manager() -> TempFileManager:
    """获取全局临时文件管理器"""
    global _temp_manager
    if _temp_manager is None:
        _temp_manager = TempFileManager()
    return _temp_manager


def cleanup_old_temp_files(hours: int = 24):
    """清理超过指定小时数的临时文件"""
    manager = get_temp_manager()
    manager.clean_temp_files(older_than_hours=hours)

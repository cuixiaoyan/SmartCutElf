"""
文件管理模块
负责扫描、验证和管理视频文件
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import LoggerMixin


class FileManager(LoggerMixin):
    """文件管理器"""
    
    # 支持的视频格式
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm']
    
    def __init__(self):
        """初始化文件管理器"""
        super().__init__()
    
    def scan_video_files(self, folder_path: str, recursive: bool = True) -> List[Dict]:
        """
        扫描文件夹中的视频文件
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归扫描子文件夹
            
        Returns:
            视频文件信息列表
        """
        self.logger.info(f"开始扫描视频文件: {folder_path}")
        
        video_files = []
        folder = Path(folder_path)
        
        if not folder.exists():
            self.logger.error(f"文件夹不存在: {folder_path}")
            return video_files
        
        if not folder.is_dir():
            self.logger.error(f"路径不是文件夹: {folder_path}")
            return video_files
        
        # 扫描文件
        if recursive:
            files = folder.rglob('*')
        else:
            files = folder.glob('*')
        
        for file_path in files:
            if file_path.is_file() and self.is_video_file(file_path):
                try:
                    file_info = self._get_file_info(file_path)
                    video_files.append(file_info)
                    self.logger.debug(f"找到视频文件: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"获取文件信息失败 {file_path}: {e}")
        
        self.logger.info(f"扫描完成，找到 {len(video_files)} 个视频文件")
        return video_files
    
    def is_video_file(self, file_path: Path) -> bool:
        """
        判断文件是否为支持的视频格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为视频文件
        """
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def _get_file_info(self, file_path: Path) -> Dict:
        """
        获取文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        stat = file_path.stat()
        
        return {
            'path': str(file_path.absolute()),
            'name': file_path.name,
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'extension': file_path.suffix.lower(),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime)
        }
    
    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        验证文件是否可以处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            return False, "文件不存在"
        
        # 检查是否为文件
        if not path.is_file():
            return False, "不是有效的文件"
        
        # 检查格式
        if not self.is_video_file(path):
            return False, f"不支持的格式 {path.suffix}"
        
        # 检查文件大小
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb < 0.1:
            return False, "文件太小，可能已损坏"
        
        # 检查文件是否可读
        try:
            with open(path, 'rb') as f:
                f.read(1024)
        except Exception as e:
            return False, f"文件无法读取: {e}"
        
        return True, None
    
    def create_output_path(self, input_path: str, output_dir: str, suffix: str = "_edited") -> str:
        """
        创建输出文件路径
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            suffix: 文件名后缀
            
        Returns:
            输出文件路径
        """
        input_file = Path(input_path)
        output_folder = Path(output_dir)
        
        # 创建输出目录
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件名
        output_name = f"{input_file.stem}{suffix}{input_file.suffix}"
        output_path = output_folder / output_name
        
        # 如果文件已存在，添加数字后缀
        counter = 1
        while output_path.exists():
            output_name = f"{input_file.stem}{suffix}_{counter}{input_file.suffix}"
            output_path = output_folder / output_name
            counter += 1
        
        return str(output_path)
    
    def cleanup_temp_files(self, temp_dir: str):
        """
        清理临时文件
        
        Args:
            temp_dir: 临时文件目录
        """
        temp_path = Path(temp_dir)
        
        if not temp_path.exists():
            return
        
        try:
            import shutil
            shutil.rmtree(temp_path)
            self.logger.info(f"临时文件已清理: {temp_dir}")
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {e}")
    
    def get_file_count(self, folder_path: str) -> int:
        """
        获取文件夹中视频文件数量
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            文件数量
        """
        files = self.scan_video_files(folder_path)
        return len(files)

"""
文件管理器测试
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """文件管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.file_manager = FileManager()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_scan_video_files_empty_folder(self):
        """测试扫描空文件夹"""
        result = self.file_manager.scan_video_files(self.test_dir)
        self.assertEqual(len(result), 0)
    
    def test_scan_video_files_with_videos(self):
        """测试扫描包含视频文件的文件夹"""
        # 创建测试文件
        test_files = ['test1.mp4', 'test2.avi', 'test3.mov', 'not_video.txt']
        for file in test_files:
            file_path = os.path.join(self.test_dir, file)
            with open(file_path, 'wb') as f:
                f.write(b'test content')
        
        result = self.file_manager.scan_video_files(self.test_dir)
        
        # 应该只找到3个视频文件
        self.assertEqual(len(result), 3)
        
        # 验证文件名
        file_names = [f['name'] for f in result]
        self.assertIn('test1.mp4', file_names)
        self.assertIn('test2.avi', file_names)
        self.assertIn('test3.mov', file_names)
        self.assertNotIn('not_video.txt', file_names)
    
    def test_scan_video_files_nested_folders(self):
        """测试扫描嵌套文件夹"""
        # 创建嵌套目录
        nested_dir = os.path.join(self.test_dir, 'subfolder')
        os.makedirs(nested_dir)
        
        # 在不同层级创建视频文件
        with open(os.path.join(self.test_dir, 'video1.mp4'), 'wb') as f:
            f.write(b'test')
        with open(os.path.join(nested_dir, 'video2.mp4'), 'wb') as f:
            f.write(b'test')
        
        result = self.file_manager.scan_video_files(self.test_dir)
        
        # 应该找到两个视频文件
        self.assertEqual(len(result), 2)
    
    def test_get_video_info(self):
        """测试获取视频文件信息"""
        # 创建测试文件
        test_file = os.path.join(self.test_dir, 'test.mp4')
        test_content = b'test video content'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        result = self.file_manager.scan_video_files(self.test_dir)
        
        self.assertEqual(len(result), 1)
        video_info = result[0]
        
        # 验证信息字段
        self.assertIn('name', video_info)
        self.assertIn('path', video_info)
        self.assertIn('size', video_info)
        self.assertIn('size_mb', video_info)
        self.assertIn('extension', video_info)
        self.assertIn('modified', video_info)
        
        # 验证文件大小
        self.assertEqual(video_info['size'], len(test_content))
        self.assertEqual(video_info['extension'], '.mp4')
    
    def test_supported_formats(self):
        """测试支持的视频格式"""
        supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        for fmt in supported_formats:
            test_file = os.path.join(self.test_dir, f'test{fmt}')
            with open(test_file, 'wb') as f:
                f.write(b'test')
        
        result = self.file_manager.scan_video_files(self.test_dir)
        
        # 应该找到所有支持格式的文件
        self.assertEqual(len(result), len(supported_formats))


if __name__ == '__main__':
    unittest.main()

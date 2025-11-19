"""
数据库管理模块
使用SQLite存储项目信息、处理结果和错误日志
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "smartcutelf.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settings TEXT
                )
            ''')
            
            # 创建文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    duration REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # 创建处理结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    output_path TEXT,
                    processing_time REAL,
                    highlights TEXT,
                    subtitles TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')
            
            # 创建错误日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_project(self, name: str, settings: Dict = None) -> int:
        """
        创建新项目
        
        Args:
            name: 项目名称
            settings: 项目设置
            
        Returns:
            项目ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO projects (name, settings) VALUES (?, ?)',
                (name, json.dumps(settings) if settings else None)
            )
            conn.commit()
            return cursor.lastrowid
    
    def add_file(self, project_id: int, file_path: str, file_name: str, 
                 file_size: int, duration: float = None) -> int:
        """
        添加文件记录
        
        Args:
            project_id: 项目ID
            file_path: 文件路径
            file_name: 文件名
            file_size: 文件大小（字节）
            duration: 视频时长（秒）
            
        Returns:
            文件ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO files 
                   (project_id, file_path, file_name, file_size, duration)
                   VALUES (?, ?, ?, ?, ?)''',
                (project_id, file_path, file_name, file_size, duration)
            )
            conn.commit()
            return cursor.lastrowid
    
    def update_file_status(self, file_id: int, status: str):
        """
        更新文件状态
        
        Args:
            file_id: 文件ID
            status: 状态 (pending, processing, completed, failed)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE files SET status = ? WHERE id = ?',
                (status, file_id)
            )
            conn.commit()
    
    def save_processing_result(self, file_id: int, output_path: str,
                               processing_time: float, highlights: List = None,
                               subtitles: List = None) -> int:
        """
        保存处理结果
        
        Args:
            file_id: 文件ID
            output_path: 输出文件路径
            processing_time: 处理时间（秒）
            highlights: 高光片段信息
            subtitles: 字幕信息
            
        Returns:
            结果ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO processing_results
                   (file_id, output_path, processing_time, highlights, subtitles)
                   VALUES (?, ?, ?, ?, ?)''',
                (file_id, output_path, processing_time,
                 json.dumps(highlights) if highlights else None,
                 json.dumps(subtitles) if subtitles else None)
            )
            conn.commit()
            return cursor.lastrowid
    
    def log_error(self, file_id: int, error_type: str, error_message: str,
                  stack_trace: str = None):
        """
        记录错误日志
        
        Args:
            file_id: 文件ID
            error_type: 错误类型
            error_message: 错误消息
            stack_trace: 堆栈跟踪
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO error_logs
                   (file_id, error_type, error_message, stack_trace)
                   VALUES (?, ?, ?, ?)''',
                (file_id, error_type, error_message, stack_trace)
            )
            conn.commit()
    
    def get_files_by_project(self, project_id: int) -> List[Dict]:
        """
        获取项目的所有文件
        
        Args:
            project_id: 项目ID
            
        Returns:
            文件列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM files WHERE project_id = ?',
                (project_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_processing_result(self, file_id: int) -> Optional[Dict]:
        """
        获取文件的处理结果
        
        Args:
            file_id: 文件ID
            
        Returns:
            处理结果字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM processing_results WHERE file_id = ? ORDER BY created_at DESC LIMIT 1',
                (file_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get('highlights'):
                    result['highlights'] = json.loads(result['highlights'])
                if result.get('subtitles'):
                    result['subtitles'] = json.loads(result['subtitles'])
                return result
            return None


# 全局数据库实例
_db_instance = None


def get_database() -> DatabaseManager:
    """获取全局数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance

"""
配置管理模块
负责加载、保存和管理应用程序配置
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        # 基本设置
        "app": {
            "name": "SmartCutElf",
            "version": "1.0.0",
            "language": "zh_CN"
        },
        
        # 处理设置
        "processing": {
            "max_workers": 4,
            "target_duration_min": 180,  # 3分钟
            "target_duration_max": 300,  # 5分钟
            "segment_duration": 10,  # 片段分析时长（秒）
            "auto_delete_temp": True
        },
        
        # 输出设置
        "output": {
            "folder": "output",
            "format": "mp4",
            "resolution": "1080p",
            "fps": 30,
            "video_codec": "libx264",
            "audio_codec": "aac",
            "bitrate": "5000k"
        },
        
        # 高光检测设置
        "highlight": {
            "sensitivity": "medium",  # low, medium, high
            "audio_weight": 0.4,
            "video_weight": 0.4,
            "time_weight": 0.2
        },
        
        # 字幕设置
        "subtitle": {
            "enabled": True,
            "font_name": "Microsoft YaHei",
            "font_size": "medium",  # small, medium, large
            "font_color": "white",
            "position": "bottom",
            "outline": True,
            "outline_color": "black"
        },
        
        # 语音设置
        "speech": {
            "recognition_model": "base",  # tiny, base, small, medium, large
            "tts_enabled": False,
            "tts_voice": "female",
            "background_music": False,
            "music_volume": 30
        },
        
        # UI设置
        "ui": {
            "theme": "dark",  # light, dark
            "window_width": 1200,
            "window_height": 800
        },
        
        # 性能设置
        "performance": {
            "memory_limit_mb": 2048,
            "cache_enabled": True,
            "cache_size_mb": 500
        }
    }
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        
    def load(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix == '.yaml' or self.config_file.suffix == '.yml':
                        self.config = yaml.safe_load(f)
                    else:
                        self.config = json.load(f)
                print(f"配置已加载: {self.config_file}")
            except Exception as e:
                print(f"加载配置失败: {e}，使用默认配置")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            print("配置文件不存在，使用默认配置")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.suffix == '.yaml' or self.config_file.suffix == '.yml':
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
                else:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置已保存: {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，使用.分隔，如 "processing.max_workers"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()


# 全局配置实例
_config_instance = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        _config_instance.load()
    return _config_instance

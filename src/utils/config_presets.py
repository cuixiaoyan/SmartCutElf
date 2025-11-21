"""
配置预设管理
提供快速、标准、高质量等预定义配置模板
"""

from typing import Dict, Any


class ConfigPresets:
    """配置预设集合"""
    
    # 快速模式 - 适合快速预览和测试
    PRESET_FAST = {
        "name": "快速模式",
        "description": "快速处理，适合预览和测试",
        "settings": {
            "processing": {
                "max_workers": 2,
                "target_duration_min": 120,
                "target_duration_max": 180,
            },
            "output": {
                "resolution": "720p",
                "fps": 25,
                "video_codec": "libx264",
                "preset": "ultrafast",
                "crf": "28",
                "bitrate": "2000k"
            },
            "speech": {
                "recognition_model": "tiny",
            },
            "subtitle": {
                "enabled": False,
            }
        }
    }
    
    # 标准模式 - 平衡质量和速度
    PRESET_STANDARD = {
        "name": "标准模式",
        "description": "平衡质量与速度，适合日常使用",
        "settings": {
            "processing": {
                "max_workers": 4,
                "target_duration_min": 180,
                "target_duration_max": 300,
            },
            "output": {
                "resolution": "1080p",
                "fps": 30,
                "video_codec": "libx264",
                "preset": "medium",
                "crf": "23",
                "bitrate": "5000k"
            },
            "speech": {
                "recognition_model": "base",
            },
            "subtitle": {
                "enabled": True,
            }
        }
    }
    
    # 高质量模式 - 最佳输出质量
    PRESET_HIGH_QUALITY = {
        "name": "高质量模式",
        "description": "最佳输出质量，处理时间较长",
        "settings": {
            "processing": {
                "max_workers": 6,
                "target_duration_min": 240,
                "target_duration_max": 360,
            },
            "output": {
                "resolution": "1080p",
                "fps": 60,
                "video_codec": "libx264",
                "preset": "slow",
                "crf": "18",
                "bitrate": "8000k"
            },
            "speech": {
                "recognition_model": "small",
            },
            "subtitle": {
                "enabled": True,
                "font_size": "large",
            }
        }
    }
    
    # 短视频模式 - 适合抖音、快手等平台
    PRESET_SHORT_VIDEO = {
        "name": "短视频模式",
        "description": "竖屏短视频，适合抖音/快手",
        "settings": {
            "processing": {
                "max_workers": 4,
                "target_duration_min": 30,
                "target_duration_max": 60,
            },
            "output": {
                "resolution": "1080x1920",  # 竖屏
                "fps": 30,
                "video_codec": "libx264",
                "preset": "fast",
                "crf": "23",
                "bitrate": "6000k"
            },
            "speech": {
                "recognition_model": "base",
            },
            "subtitle": {
                "enabled": True,
                "font_size": "large",
                "position": "center",
            }
        }
    }
    
    # B站模式 - 适合B站投稿
    PRESET_BILIBILI = {
        "name": "B站模式",
        "description": "适合B站投稿要求",
        "settings": {
            "processing": {
                "max_workers": 4,
                "target_duration_min": 300,
                "target_duration_max": 600,
            },
            "output": {
                "resolution": "1080p",
                "fps": 60,
                "video_codec": "libx264",
                "preset": "medium",
                "crf": "20",
                "bitrate": "8000k"
            },
            "speech": {
                "recognition_model": "base",
            },
            "subtitle": {
                "enabled": True,
            }
        }
    }
    
    @classmethod
    def get_all_presets(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有预设"""
        return {
            "fast": cls.PRESET_FAST,
            "standard": cls.PRESET_STANDARD,
            "high_quality": cls.PRESET_HIGH_QUALITY,
            "short_video": cls.PRESET_SHORT_VIDEO,
            "bilibili": cls.PRESET_BILIBILI,
        }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Dict[str, Any]:
        """
        获取指定预设
        
        Args:
            preset_name: 预设名称 (fast/standard/high_quality/short_video/bilibili)
        
        Returns:
            预设配置字典
        """
        presets = cls.get_all_presets()
        return presets.get(preset_name, cls.PRESET_STANDARD)
    
    @classmethod
    def apply_preset(cls, config, preset_name: str):
        """
        应用预设到配置对象
        
        Args:
            config: Config对象
            preset_name: 预设名称
        """
        preset = cls.get_preset(preset_name)
        settings = preset.get("settings", {})
        
        # 递归应用设置
        for category, values in settings.items():
            for key, value in values.items():
                config.set(f"{category}.{key}", value)
        
        # 保存配置
        config.save()
        
        return preset.get("name", "未知预设")

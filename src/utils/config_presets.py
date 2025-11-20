"""
配置预设管理
提供快速、平衡、高质量等预设模式
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ConfigPreset:
    """配置预设"""
    name: str
    description: str
    icon: str
    settings: Dict
    
    def apply_to_config(self, config) -> None:
        """应用预设到配置"""
        for key, value in self.settings.items():
            config.set(key, value)


class PresetManager:
    """预设管理器"""
    
    # 预设定义
    PRESETS = {
        "fast": ConfigPreset(
            name="快速模式",
            description="快速处理，适合预览和测试",
            icon="⚡",
            settings={
                # 处理设置
                "processing.max_workers": 8,
                "processing.target_duration_min": 120,
                "processing.target_duration_max": 180,
                "processing.transition_enabled": False,
                
                # 高光检测
                "highlight.audio_weight": 0.5,
                "highlight.video_weight": 0.3,
                "highlight.time_weight": 0.2,
                "highlight.min_segment_duration": 3,
                "highlight.max_segment_duration": 15,
                
                # AI 设置
                "speech.recognition_model": "tiny",
                "speech.tts_enabled": False,
                "subtitle.enabled": False,
                
                # 输出设置
                "output.video_codec": "libx264",
                "output.video_bitrate": "2M",
                "output.audio_bitrate": "128k",
                "output.preset": "ultrafast"
            }
        ),
        
        "balanced": ConfigPreset(
            name="平衡模式",
            description="平衡速度和质量，日常使用推荐",
            icon="⚖️",
            settings={
                # 处理设置
                "processing.max_workers": 4,
                "processing.target_duration_min": 180,
                "processing.target_duration_max": 300,
                "processing.transition_enabled": True,
                "processing.transition_type": "fade",
                "processing.transition_duration": 0.5,
                
                # 高光检测
                "highlight.audio_weight": 0.4,
                "highlight.video_weight": 0.4,
                "highlight.time_weight": 0.2,
                "highlight.min_segment_duration": 5,
                "highlight.max_segment_duration": 20,
                
                # AI 设置
                "speech.recognition_model": "base",
                "speech.tts_enabled": True,
                "subtitle.enabled": True,
                
                # 输出设置
                "output.video_codec": "libx264",
                "output.video_bitrate": "4M",
                "output.audio_bitrate": "192k",
                "output.preset": "medium"
            }
        ),
        
        "quality": ConfigPreset(
            name="高质量模式",
            description="最佳质量，处理时间较长",
            icon="💎",
            settings={
                # 处理设置
                "processing.max_workers": 2,
                "processing.target_duration_min": 180,
                "processing.target_duration_max": 300,
                "processing.transition_enabled": True,
                "processing.transition_type": "dissolve",
                "processing.transition_duration": 1.0,
                
                # 高光检测
                "highlight.audio_weight": 0.35,
                "highlight.video_weight": 0.45,
                "highlight.time_weight": 0.2,
                "highlight.min_segment_duration": 5,
                "highlight.max_segment_duration": 30,
                
                # AI 设置
                "speech.recognition_model": "small",
                "speech.tts_enabled": True,
                "subtitle.enabled": True,
                
                # 输出设置
                "output.video_codec": "libx264",
                "output.video_bitrate": "8M",
                "output.audio_bitrate": "320k",
                "output.preset": "slow"
            }
        ),
        
        "subtitle_only": ConfigPreset(
            name="仅字幕模式",
            description="只生成字幕，不剪辑视频",
            icon="📝",
            settings={
                # 处理设置
                "processing.max_workers": 4,
                "processing.target_duration_min": 0,  # 不剪辑
                "processing.target_duration_max": 999999,
                "processing.transition_enabled": False,
                
                # 高光检测（不使用）
                "highlight.audio_weight": 0,
                "highlight.video_weight": 0,
                "highlight.time_weight": 0,
                
                # AI 设置
                "speech.recognition_model": "base",
                "speech.tts_enabled": False,
                "subtitle.enabled": True,
                
                # 输出设置
                "output.video_codec": "copy",  # 不重新编码
                "output.audio_codec": "copy"
            }
        ),
        
        "short_video": ConfigPreset(
            name="短视频模式",
            description="适合抖音、快手等短视频平台",
            icon="📱",
            settings={
                # 处理设置
                "processing.max_workers": 4,
                "processing.target_duration_min": 30,
                "processing.target_duration_max": 60,
                "processing.orientation": "vertical",  # 竖屏
                "processing.transition_enabled": True,
                "processing.transition_type": "slide_up",
                "processing.transition_duration": 0.3,
                
                # 高光检测
                "highlight.audio_weight": 0.5,
                "highlight.video_weight": 0.4,
                "highlight.time_weight": 0.1,
                "highlight.min_segment_duration": 3,
                "highlight.max_segment_duration": 10,
                
                # AI 设置
                "speech.recognition_model": "base",
                "speech.tts_enabled": True,
                "subtitle.enabled": True,
                "subtitle.font_size": 48,  # 大字体
                
                # 输出设置
                "output.video_codec": "libx264",
                "output.video_bitrate": "6M",
                "output.audio_bitrate": "192k",
                "output.resolution": "1080x1920"  # 竖屏分辨率
            }
        ),
        
        "long_video": ConfigPreset(
            name="长视频模式",
            description="适合 B站、YouTube 等长视频平台",
            icon="🎬",
            settings={
                # 处理设置
                "processing.max_workers": 2,
                "processing.target_duration_min": 300,
                "processing.target_duration_max": 600,
                "processing.orientation": "horizontal",  # 横屏
                "processing.transition_enabled": True,
                "processing.transition_type": "fade",
                "processing.transition_duration": 0.8,
                
                # 高光检测
                "highlight.audio_weight": 0.4,
                "highlight.video_weight": 0.4,
                "highlight.time_weight": 0.2,
                "highlight.min_segment_duration": 10,
                "highlight.max_segment_duration": 60,
                
                # AI 设置
                "speech.recognition_model": "base",
                "speech.tts_enabled": True,
                "subtitle.enabled": True,
                
                # 输出设置
                "output.video_codec": "libx264",
                "output.video_bitrate": "8M",
                "output.audio_bitrate": "256k",
                "output.resolution": "1920x1080"
            }
        )
    }
    
    @classmethod
    def get_preset(cls, preset_id: str) -> ConfigPreset:
        """获取预设"""
        return cls.PRESETS.get(preset_id)
    
    @classmethod
    def get_all_presets(cls) -> List[ConfigPreset]:
        """获取所有预设"""
        return list(cls.PRESETS.values())
    
    @classmethod
    def get_preset_names(cls) -> List[str]:
        """获取所有预设名称"""
        return [preset.name for preset in cls.PRESETS.values()]
    
    @classmethod
    def apply_preset(cls, preset_id: str, config) -> bool:
        """
        应用预设
        
        Args:
            preset_id: 预设ID
            config: 配置对象
            
        Returns:
            是否成功
        """
        preset = cls.get_preset(preset_id)
        if not preset:
            return False
        
        preset.apply_to_config(config)
        return True
    
    @classmethod
    def get_preset_comparison(cls) -> str:
        """获取预设对比表"""
        comparison = "# 预设模式对比\n\n"
        comparison += "| 模式 | 速度 | 质量 | 字幕 | 适用场景 |\n"
        comparison += "|------|------|------|------|----------|\n"
        
        preset_info = {
            "fast": ("⚡⚡⚡", "⭐⭐", "❌", "快速预览、测试"),
            "balanced": ("⚡⚡", "⭐⭐⭐", "✅", "日常使用"),
            "quality": ("⚡", "⭐⭐⭐⭐⭐", "✅", "高质量输出"),
            "subtitle_only": ("⚡⚡⚡", "-", "✅", "仅生成字幕"),
            "short_video": ("⚡⚡", "⭐⭐⭐", "✅", "抖音、快手"),
            "long_video": ("⚡", "⭐⭐⭐⭐", "✅", "B站、YouTube")
        }
        
        for preset_id, preset in cls.PRESETS.items():
            info = preset_info.get(preset_id, ("", "", "", ""))
            comparison += f"| {preset.icon} {preset.name} | {info[0]} | {info[1]} | {info[2]} | {info[3]} |\n"
        
        return comparison


class CustomPreset:
    """自定义预设"""
    
    @staticmethod
    def save_custom_preset(name: str, description: str, config, preset_file: str = "config/custom_presets.json"):
        """保存自定义预设"""
        import json
        from pathlib import Path
        
        preset_path = Path(preset_file)
        preset_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取现有预设
        presets = {}
        if preset_path.exists():
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
            except:
                pass
        
        # 添加新预设
        presets[name] = {
            "description": description,
            "settings": config.to_dict()
        }
        
        # 保存
        with open(preset_path, 'w', encoding='utf-8') as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_custom_presets(preset_file: str = "config/custom_presets.json") -> Dict:
        """加载自定义预设"""
        import json
        from pathlib import Path
        
        preset_path = Path(preset_file)
        if not preset_path.exists():
            return {}
        
        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

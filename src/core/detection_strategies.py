"""
视频高光检测策略模式
为不同类型视频提供定制化的高光检测策略
"""

import sys
from pathlib import Path
# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from enum import Enum
from utils.logger import LoggerMixin


class VideoType(Enum):
    """视频类型枚举"""
    GAME = "game"           # 游戏视频
    VLOG = "vlog"           # Vlog/生活记录
    EDUCATION = "education" # 教育教学
    SPORTS = "sports"       # 体育竞技
    TALK = "talk"           # 访谈/对话
    MUSIC = "music"         # 音乐/表演
    GENERIC = "generic"     # 通用/未分类


class DetectionStrategy(LoggerMixin, ABC):
    """高光检测策略基类"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Base"

    @abstractmethod
    def get_weights(self) -> Dict[str, float]:
        """
        获取权重配置

        Returns:
            包含 audio_weight, video_weight, time_weight 的字典
        """
        pass

    @abstractmethod
    def get_detection_params(self, video_info: Dict) -> Dict:
        """
        获取检测参数

        Args:
            video_info: 视频信息字典

        Returns:
            包含 segment_duration, target_duration_min 等的字典
        """
        pass

    @abstractmethod
    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        """
        判断是否应该包含某个片段

        Args:
            segment: 片段信息
            context: 上下文信息

        Returns:
            是否包含该片段
        """
        pass

    def adjust_score(self, base_score: float, segment: Dict, context: Dict) -> float:
        """
        调整基础分数

        Args:
            base_score: 基础分数
            segment: 片段信息
            context: 上下文信息

        Returns:
            调整后的分数
        """
        return base_score


class GameDetectionStrategy(DetectionStrategy):
    """游戏视频检测策略 - 专注于击杀、高光操作"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Game"

    def get_weights(self) -> Dict[str, float]:
        return {
            'audio_weight': 0.5,   # 游戏中音效变化很重要
            'video_weight': 0.4,   # 画面变化
            'time_weight': 0.1     # 不太在意时间位置
        }

    def get_detection_params(self, video_info: Dict) -> Dict:
        duration = video_info.get('duration', 300)
        return {
            'segment_duration': 5,    # 更短的分段，捕捉快速操作
            'target_duration_min': max(60, duration * 0.2),
            'target_duration_max': max(120, duration * 0.4)
        }

    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        # 游戏视频倾向于包含高分片段，即使时长较短
        return segment.get('score', 0) > 0.3

    def adjust_score(self, base_score: float, segment: Dict, context: Dict) -> float:
        # 运动强度大的片段加分（可能是击杀时刻）
        motion_intensity = segment.get('motion_intensity', 0)
        if motion_intensity > 0.7:
            return min(base_score * 1.3, 1.0)
        return base_score


class VlogDetectionStrategy(DetectionStrategy):
    """Vlog检测策略 - 专注于情感表达和场景变化"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Vlog"

    def get_weights(self) -> Dict[str, float]:
        return {
            'audio_weight': 0.3,   # 人声重要但不是全部
            'video_weight': 0.5,   # 场景变化更重要
            'time_weight': 0.2     # 时间分布
        }

    def get_detection_params(self, video_info: Dict) -> Dict:
        duration = video_info.get('duration', 300)
        return {
            'segment_duration': 15,   # 较长分段，保留完整情节
            'target_duration_min': max(90, duration * 0.25),
            'target_duration_max': max(180, duration * 0.5)
        }

    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        score = segment.get('score', 0)
        # 避免选择太短的片段
        if segment.get('duration', 0) < 10:
            return False
        return score > 0.25

    def adjust_score(self, base_score: float, segment: Dict, context: Dict) -> float:
        # 场景变化大的片段加分
        scene_change = segment.get('scene_change', 0)
        if scene_change > 0.5:
            return min(base_score * 1.2, 1.0)
        return base_score


class EducationDetectionStrategy(DetectionStrategy):
    """教育视频检测策略 - 专注于重点知识点"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Education"

    def get_weights(self) -> Dict[str, float]:
        return {
            'audio_weight': 0.5,   # 语音最重要（讲解内容）
            'video_weight': 0.3,   # 画面辅助
            'time_weight': 0.2     # 教学逻辑顺序
        }

    def get_detection_params(self, video_info: Dict) -> Dict:
        duration = video_info.get('duration', 600)
        return {
            'segment_duration': 30,   # 长分段，保留完整讲解
            'target_duration_min': max(180, duration * 0.3),
            'target_duration_max': max(300, duration * 0.5)
        }

    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        # 教育视频优先选择高分片段，保持逻辑连贯
        return segment.get('score', 0) > 0.35

    def adjust_score(self, base_score: float, segment: Dict, context: Dict) -> float:
        # 音频活跃度高（在讲解）加分
        audio_activity = segment.get('audio_activity', 0)
        if audio_activity > 0.6:
            return min(base_score * 1.15, 1.0)
        return base_score


class SportsDetectionStrategy(DetectionStrategy):
    """体育竞技检测策略 - 专注于精彩瞬间"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Sports"

    def get_weights(self) -> Dict[str, float]:
        return {
            'audio_weight': 0.5,   # 解说和观众反应
            'video_weight': 0.4,   # 画面动作
            'time_weight': 0.1     # 不考虑时间位置
        }

    def get_detection_params(self, video_info: Dict) -> Dict:
        duration = video_info.get('duration', 180)
        return {
            'segment_duration': 3,     # 极短分段，捕捉瞬间
            'target_duration_min': max(45, duration * 0.25),
            'target_duration_max': max(90, duration * 0.5)
        }

    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        # 体育视频只选最精彩的部分
        return segment.get('score', 0) > 0.5

    def adjust_score(self, base_score: float, segment: Dict, context: Dict) -> float:
        # 高音量（欢呼/解说）和高运动同时出现大幅加分
        if segment.get('energy', 0) > 0.7 and segment.get('motion', 0) > 0.6:
            return min(base_score * 1.5, 1.0)
        return base_score


class GenericDetectionStrategy(DetectionStrategy):
    """通用检测策略 - 平衡所有因素"""

    def __init__(self):
        super().__init__()
        self.strategy_name = "Generic"

    def get_weights(self) -> Dict[str, float]:
        return {
            'audio_weight': 0.4,
            'video_weight': 0.4,
            'time_weight': 0.2
        }

    def get_detection_params(self, video_info: Dict) -> Dict:
        duration = video_info.get('duration', 300)
        return {
            'segment_duration': 10,
            'target_duration_min': max(60, duration * 0.3),
            'target_duration_max': max(180, duration * 0.6)
        }

    def should_include_segment(self, segment: Dict, context: Dict) -> bool:
        return segment.get('score', 0) > 0.3


class StrategyFactory:
    """策略工厂"""

    _strategies = {
        VideoType.GAME: GameDetectionStrategy,
        VideoType.VLOG: VlogDetectionStrategy,
        VideoType.EDUCATION: EducationDetectionStrategy,
        VideoType.SPORTS: SportsDetectionStrategy,
        VideoType.TALK: EducationDetectionStrategy,  # 使用教育策略
        VideoType.MUSIC: VlogDetectionStrategy,      # 使用Vlog策略
        VideoType.GENERIC: GenericDetectionStrategy
    }

    @classmethod
    def create_strategy(cls, video_type: VideoType) -> DetectionStrategy:
        """创建策略实例"""
        strategy_class = cls._strategies.get(video_type, GenericDetectionStrategy)
        return strategy_class()

    @classmethod
    def get_available_types(cls) -> List[VideoType]:
        """获取所有可用的视频类型"""
        return list(cls._strategies.keys())


class VideoTypeDetector(LoggerMixin):
    """视频类型自动检测器"""

    def __init__(self):
        super().__init__()

    def detect_type(self, video_path: str, video_info: Dict = None,
                    filename: str = None) -> VideoType:
        """
        检测视频类型

        Args:
            video_path: 视频路径
            video_info: 视频信息
            filename: 文件名

        Returns:
            检测到的视频类型
        """
        # 从文件名推断
        if filename:
            filename_lower = filename.lower()

            # 游戏关键词
            game_keywords = ['game', '游戏', 'play', 'gameplay', 'gaming',
                           'lol', 'dota', 'csgo', 'pubg', 'minecraft', '原神']
            if any(kw in filename_lower for kw in game_keywords):
                return VideoType.GAME

            # Vlog关键词
            vlog_keywords = ['vlog', 'daily', '日常', 'life', '生活', 'travel', '旅行',
                           'food', '美食', 'review', '评测', 'unbox', '开箱']
            if any(kw in filename_lower for kw in vlog_keywords):
                return VideoType.VLOG

            # 教育关键词
            edu_keywords = ['tutorial', '教程', 'course', '课程', 'learn', '学习',
                          'how to', '如何', 'guide', '指南', 'explain', '讲解']
            if any(kw in filename_lower for kw in edu_keywords):
                return VideoType.EDUCATION

            # 体育关键词
            sports_keywords = ['sport', '体育', 'football', 'soccer', 'basketball',
                             'nba', 'world cup', '世界杯', 'olympic', '奥运']
            if any(kw in filename_lower for kw in sports_keywords):
                return VideoType.SPORTS

            # 音乐关键词
            music_keywords = ['music', '音乐', 'mv', 'cover', '翻唱', 'concert',
                            '演唱会', 'dance', '舞蹈', 'performance']
            if any(kw in filename_lower for kw in music_keywords):
                return VideoType.MUSIC

            # 访谈关键词
            talk_keywords = ['talk', '访谈', 'interview', 'podcast', '播客',
                           'conversation', '对话', 'debate', '辩论']
            if any(kw in filename_lower for kw in talk_keywords):
                return VideoType.TALK

        # 从时长推断
        if video_info:
            duration = video_info.get('duration', 0)
            # 短视频可能是Vlog或游戏
            if duration < 120:
                return VideoType.VLOG
            # 长视频可能是教育或游戏
            elif duration > 1200:
                return VideoType.EDUCATION

        # 默认通用类型
        return VideoType.GENERIC

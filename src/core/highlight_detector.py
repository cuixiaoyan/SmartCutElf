"""
高光检测引擎
综合音频和视频分析，智能检测精彩片段
"""

import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from core.audio_analyzer import AudioAnalyzer
from core.video_analyzer import VideoAnalyzer
from core.video_processor import VideoProcessor
from utils.logger import LoggerMixin


class HighlightDetector(LoggerMixin):
    """高光检测器"""
    
    def __init__(self, audio_weight: float = 0.4, 
                 video_weight: float = 0.4,
                 time_weight: float = 0.2):
        """
        初始化高光检测器
        
        Args:
            audio_weight: 音频权重
            video_weight: 视频权重
            time_weight: 时间分布权重
        """
        super().__init__()
        self.audio_weight = audio_weight
        self.video_weight = video_weight
        self.time_weight = time_weight
        
        self.audio_analyzer = AudioAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.video_processor = VideoProcessor()
    
    def analyze_video(self, video_path: str, segment_duration: float = 10.0) -> List[Dict]:
        """
        分析视频，将其分段并计算每段的兴趣度分数
        
        Args:
            video_path: 视频文件路径
            segment_duration: 分段时长（秒）
            
        Returns:
            分段分析结果列表
        """
        self.logger.info(f"开始分析视频: {video_path}")
        
        # 获取视频信息
        video_info = self.video_processor.get_video_info(video_path)
        if not video_info:
            self.logger.error("无法获取视频信息")
            return []
        
        total_duration = video_info['duration']
        self.logger.info(f"视频总时长: {total_duration:.2f}秒")
        
        # 提取音频
        temp_audio_path = Path(video_path).parent / "temp_audio.wav"
        if not self.video_processor.extract_audio(video_path, str(temp_audio_path)):
            self.logger.error("音频提取失败")
            return []
        
        # 分段分析
        segments = []
        num_segments = int(np.ceil(total_duration / segment_duration))
        
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, total_duration)
            
            # 计算综合分数
            score = self.calculate_segment_score(
                video_path, 
                str(temp_audio_path),
                start_time, 
                end_time, 
                total_duration
            )
            
            segments.append({
                'index': i,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'score': score
            })
            
            self.logger.debug(f"片段 {i+1}/{num_segments}: {start_time:.1f}s-{end_time:.1f}s, 分数: {score:.3f}")
        
        # 清理临时文件
        if temp_audio_path.exists():
            temp_audio_path.unlink()
        
        # 按分数排序
        segments.sort(key=lambda x: x['score'], reverse=True)
        
        self.logger.info(f"视频分析完成，共 {len(segments)} 个片段")
        return segments
    
    def calculate_segment_score(self, video_path: str, audio_path: str,
                               start_time: float, end_time: float,
                               total_duration: float) -> float:
        """
        计算单个片段的综合分数
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            start_time: 片段开始时间
            end_time: 片段结束时间
            total_duration: 视频总时长
            
        Returns:
            综合分数（0-1）
        """
        # 音频分数
        audio_score = self.audio_analyzer.calculate_audio_score(
            audio_path, start_time, end_time
        )
        
        # 视频分数
        video_score = self.video_analyzer.calculate_video_score(
            video_path, start_time, end_time
        )
        
        # 时间位置分数（避免过度偏向开头和结尾）
        time_position = (start_time + end_time) / 2
        normalized_position = time_position / total_duration if total_duration > 0 else 0.5
        time_score = 1 - abs(normalized_position - 0.5) * 2
        
        # 综合分数
        composite_score = (
            audio_score * self.audio_weight +
            video_score * self.video_weight +
            time_score * self.time_weight
        )
        
        return min(composite_score, 1.0)
    
    def select_highlights(self, segments: List[Dict], 
                         target_duration: float,
                         min_segment_duration: float = 5.0) -> List[Dict]:
        """
        从分段中选择高光片段
        
        Args:
            segments: 分段分析结果
            target_duration: 目标总时长（秒）
            min_segment_duration: 最小片段时长（秒）
            
        Returns:
            选中的高光片段列表
        """
        self.logger.info(f"开始选择高光片段，目标时长: {target_duration}秒")
        
        # 过滤太短的片段
        valid_segments = [s for s in segments if s['duration'] >= min_segment_duration]
        
        # 按分数排序
        sorted_segments = sorted(valid_segments, key=lambda x: x['score'], reverse=True)
        
        selected = []
        current_duration = 0
        
        for segment in sorted_segments:
            if current_duration + segment['duration'] <= target_duration:
                selected.append(segment)
                current_duration += segment['duration']
                self.logger.debug(f"选择片段: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s")
            
            if current_duration >= target_duration * 0.95:  # 达到目标的95%即可
                break
        
        # 按时间顺序排序
        selected.sort(key=lambda x: x['start_time'])
        
        total_duration = sum(s['duration'] for s in selected)
        self.logger.info(f"选择了 {len(selected)} 个片段，总时长: {total_duration:.2f}秒")
        
        return selected
    
    def detect_highlights(self, video_path: str, 
                         target_duration_min: float = 180,
                         target_duration_max: float = 300,
                         segment_duration: float = 10.0) -> Dict:
        """
        检测视频高光片段（主方法）
        
        Args:
            video_path: 视频文件路径
            target_duration_min: 目标最小时长（秒）
            target_duration_max: 目标最大时长（秒）
            segment_duration: 分段时长（秒）
            
        Returns:
            高光检测结果
        """
        self.logger.info("="*60)
        self.logger.info("开始高光检测")
        self.logger.info("="*60)
        
        # 分析视频
        segments = self.analyze_video(video_path, segment_duration)
        
        if not segments:
            return {
                'success': False,
                'error': '视频分析失败'
            }
        
        # 选择高光片段
        target_duration = (target_duration_min + target_duration_max) / 2
        highlights = self.select_highlights(segments, target_duration)
        
        if not highlights:
            return {
                'success': False,
                'error': '未找到合适的高光片段'
            }
        
        # 准备时间段列表供视频剪辑使用
        time_ranges = [(h['start_time'], h['end_time']) for h in highlights]
        total_duration = sum(h['duration'] for h in highlights)
        
        result = {
            'success': True,
            'highlights': highlights,
            'time_ranges': time_ranges,
            'total_duration': total_duration,
            'segment_count': len(highlights),
            'average_score': np.mean([h['score'] for h in highlights])
        }
        
        self.logger.info("="*60)
        self.logger.info(f"高光检测完成 - 共 {len(highlights)} 个片段，总时长: {total_duration:.2f}秒")
        self.logger.info("="*60)
        
        return result

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
from utils.temp_file_manager import get_temp_manager


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
        
        # 使用临时文件管理器创建临时音频文件
        temp_manager = get_temp_manager()
        video_name = Path(video_path).stem
        temp_audio_path = temp_manager.create_unique_temp_file(
            prefix=f"{video_name}_",
            suffix=".wav",
            subdir="temp_audio"
        )
        
        self.logger.debug(f"临时音频文件: {temp_audio_path}")
        
        if not self.video_processor.extract_audio(video_path, str(temp_audio_path)):
            self.logger.error("音频提取失败")
            return []
        
        # 验证临时文件是否创建成功
        if not temp_audio_path.exists():
            self.logger.error(f"临时音频文件未创建: {temp_audio_path}")
            return []
        
        try:
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
            
            # 按分数排序
            segments.sort(key=lambda x: x['score'], reverse=True)
            
            self.logger.info(f"视频分析完成，共 {len(segments)} 个片段")
            return segments
            
        finally:
            # 确保清理临时文件
            try:
                if temp_audio_path.exists():
                    temp_audio_path.unlink()
                    self.logger.debug(f"已清理临时文件: {temp_audio_path}")
            except Exception as e:
                self.logger.warning(f"清理临时文件失败: {e}")
    
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
        
        if not segments:
            self.logger.warning("没有可用的片段")
            return []
        
        # 过滤太短的片段
        valid_segments = [s for s in segments if s['duration'] >= min_segment_duration]
        
        if not valid_segments:
            self.logger.warning(f"没有满足最小时长({min_segment_duration}s)的片段")
            # 如果没有满足最小时长的片段，降低标准
            valid_segments = [s for s in segments if s['duration'] >= 3.0]
            if not valid_segments:
                valid_segments = segments  # 最后手段：使用所有片段
        
        # 按分数排序
        sorted_segments = sorted(valid_segments, key=lambda x: x['score'], reverse=True)
        
        self.logger.debug(f"有效片段数: {len(valid_segments)}, 最高分数: {sorted_segments[0]['score']:.3f}")
        
        selected = []
        current_duration = 0
        min_target = target_duration * 0.8  # 最小目标时长
        max_target = target_duration * 1.2  # 最大目标时长
        
        # 第一轮：优先选择高分片段
        for segment in sorted_segments:
            if current_duration + segment['duration'] <= max_target:
                selected.append(segment)
                current_duration += segment['duration']
                self.logger.debug(
                    f"选择片段: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s, "
                    f"分数: {segment['score']:.3f}, 累计: {current_duration:.1f}s"
                )
            
            # 如果达到最小目标，检查是否可以停止
            if current_duration >= min_target:
                break
        
        # 如果时长不足，尝试添加更多片段
        if current_duration < min_target:
            self.logger.info(f"当前时长 {current_duration:.1f}s 低于最小目标 {min_target:.1f}s，尝试添加更多片段")
            
            selected_indices = {s['index'] for s in selected}
            remaining_segments = [s for s in sorted_segments if s['index'] not in selected_indices]
            
            for segment in remaining_segments:
                if current_duration + segment['duration'] <= max_target:
                    selected.append(segment)
                    current_duration += segment['duration']
                    self.logger.debug(f"补充片段: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s")
                    
                    if current_duration >= min_target:
                        break
        
        # 如果仍然不足，尝试合并相邻片段
        if current_duration < min_target and len(selected) > 0:
            selected = self._merge_adjacent_segments(selected, target_duration)
            current_duration = sum(s['duration'] for s in selected)
        
        # 按时间顺序排序
        selected.sort(key=lambda x: x['start_time'])
        
        total_duration = sum(s['duration'] for s in selected)
        self.logger.info(
            f"选择了 {len(selected)} 个片段，总时长: {total_duration:.2f}秒 "
            f"(目标: {target_duration:.1f}s, 范围: {min_target:.1f}-{max_target:.1f}s)"
        )
        
        if total_duration < min_target:
            self.logger.warning(f"警告：选择的片段总时长 ({total_duration:.1f}s) 低于最小目标 ({min_target:.1f}s)")
        
        return selected
    
    def _merge_adjacent_segments(self, segments: List[Dict], target_duration: float) -> List[Dict]:
        """
        合并相邻的片段以达到目标时长
        
        Args:
            segments: 已选择的片段列表
            target_duration: 目标时长
            
        Returns:
            合并后的片段列表
        """
        if len(segments) <= 1:
            return segments
        
        # 按时间排序
        segments.sort(key=lambda x: x['start_time'])
        
        merged = []
        current_duration = 0
        
        i = 0
        while i < len(segments) and current_duration < target_duration:
            current_segment = segments[i].copy()
            
            # 尝试与后续相邻片段合并
            j = i + 1
            while j < len(segments):
                next_segment = segments[j]
                gap = next_segment['start_time'] - current_segment['end_time']
                
                # 如果间隙小于2秒，尝试合并
                if gap <= 2.0:
                    # 合并片段
                    merged_duration = next_segment['end_time'] - current_segment['start_time']
                    if current_duration + merged_duration <= target_duration * 1.2:
                        current_segment['end_time'] = next_segment['end_time']
                        current_segment['duration'] = merged_duration
                        current_segment['score'] = (current_segment['score'] + next_segment['score']) / 2
                        j += 1
                    else:
                        break
                else:
                    break
            
            merged.append(current_segment)
            current_duration += current_segment['duration']
            i = j
        
        self.logger.debug(f"片段合并结果: {len(segments)} -> {len(merged)} 个片段")
        return merged
    
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
        self.logger.info(f"开始高光检测 - 目标时长: {target_duration_min}-{target_duration_max}秒")
        self.logger.info("="*60)
        
        # 获取视频信息用于自适应处理
        video_info = self.video_processor.get_video_info(video_path)
        if not video_info:
            return {
                'success': False,
                'error': '无法获取视频信息'
            }
        
        original_duration = video_info['duration']
        file_size_mb = video_info.get('size', 0) / (1024 * 1024)
        
        self.logger.info(f"视频信息: 时长 {original_duration:.1f}s, 文件大小 {file_size_mb:.1f}MB")
        
        # 自适应调整目标时长
        adjusted_min, adjusted_max = self._adjust_target_duration(
            original_duration, file_size_mb, target_duration_min, target_duration_max
        )
        
        self.logger.info(f"调整后目标时长: {adjusted_min:.1f}-{adjusted_max:.1f}秒")
        
        # 分析视频
        segments = self.analyze_video(video_path, segment_duration)
        
        if not segments:
            return {
                'success': False,
                'error': '视频分析失败 - 无法提取片段或分析失败'
            }
        
        self.logger.info(f"视频分析完成，共 {len(segments)} 个片段")
        
        # 显示前5个最高分数的片段
        top_segments = sorted(segments, key=lambda x: x['score'], reverse=True)[:5]
        for i, seg in enumerate(top_segments):
            self.logger.debug(
                f"Top {i+1}: {seg['start_time']:.1f}-{seg['end_time']:.1f}s, "
                f"分数: {seg['score']:.3f}, 时长: {seg['duration']:.1f}s"
            )
        
        # 使用调整后的目标时长
        target_duration = (adjusted_min + adjusted_max) / 2
        highlights = self._select_highlights_adaptive(segments, target_duration, adjusted_min, file_size_mb)
        
        if not highlights:
            return {
                'success': False,
                'error': f'未找到合适的高光片段 - 共分析了 {len(segments)} 个片段'
            }
        
        # 准备时间段列表供视频剪辑使用
        time_ranges = [(h['start_time'], h['end_time']) for h in highlights]
        total_duration = sum(h['duration'] for h in highlights)
        
        # 检查是否在调整后的目标范围内
        in_range = adjusted_min <= total_duration <= adjusted_max
        
        result = {
            'success': True,
            'highlights': highlights,
            'time_ranges': time_ranges,
            'total_duration': total_duration,
            'segment_count': len(highlights),
            'average_score': np.mean([h['score'] for h in highlights]),
            'in_target_range': in_range,
            'target_min': adjusted_min,
            'target_max': adjusted_max,
            'original_duration': original_duration,
            'file_size_mb': file_size_mb
        }
        
        self.logger.info("="*60)
        status = "✓ 在目标范围内" if in_range else "⚠ 超出目标范围"
        self.logger.info(
            f"高光检测完成 - 共 {len(highlights)} 个片段，"
            f"总时长: {total_duration:.2f}秒 {status}"
        )
        self.logger.info(
            f"平均分数: {result['average_score']:.3f}, "
            f"调整后目标: {adjusted_min:.1f}-{adjusted_max:.1f}秒"
        )
        self.logger.info("="*60)
        
        return result
    
    def _adjust_target_duration(self, original_duration: float, file_size_mb: float, 
                              target_min: float, target_max: float) -> tuple:
        """
        根据视频特征自适应调整目标时长
        
        Args:
            original_duration: 原始视频时长
            file_size_mb: 文件大小(MB)
            target_min: 原始最小目标
            target_max: 原始最大目标
            
        Returns:
            (adjusted_min, adjusted_max)
        """
        # 对于小文件或短视频，降低目标时长
        if file_size_mb < 100 or original_duration < 300:
            # 小文件策略：目标时长为原始时长的50-80%
            ratio_min = 0.5 if original_duration > 200 else 0.6
            ratio_max = 0.8 if original_duration > 200 else 0.9
            
            adjusted_min = max(60, original_duration * ratio_min)  # 最小1分钟
            adjusted_max = min(target_max, original_duration * ratio_max)
            
            # 确保最小值不超过最大值
            if adjusted_min > adjusted_max:
                adjusted_min = adjusted_max * 0.8
            
            self.logger.info(f"小文件策略: 原始{original_duration:.1f}s -> 目标{adjusted_min:.1f}-{adjusted_max:.1f}s")
            return adjusted_min, adjusted_max
        
        # 正常文件，使用原始目标
        return target_min, target_max
    
    def _select_highlights_adaptive(self, segments: List[Dict], target_duration: float, 
                                   min_duration: float, file_size_mb: float) -> List[Dict]:
        """
        自适应选择高光片段
        
        Args:
            segments: 分段列表
            target_duration: 目标时长
            min_duration: 最小时长
            file_size_mb: 文件大小
            
        Returns:
            选中的高光片段
        """
        # 对于小文件，降低质量要求
        if file_size_mb < 100:
            min_segment_duration = 3.0  # 降低最小片段时长
            self.logger.info("小文件模式: 降低质量要求")
        else:
            min_segment_duration = 5.0
        
        # 尝试正常选择
        highlights = self.select_highlights(segments, target_duration, min_segment_duration)
        
        if not highlights or sum(h['duration'] for h in highlights) < min_duration * 0.7:
            # 如果选择结果不理想，使用更宽松的策略
            self.logger.warning("正常选择不理想，使用宽松策略")
            
            # 策略1：降低最小片段时长
            highlights = self.select_highlights(segments, target_duration, 2.0)
            
            if not highlights or sum(h['duration'] for h in highlights) < min_duration * 0.5:
                # 策略2：强制选择最高分片段
                self.logger.warning("使用强制选择策略")
                sorted_segments = sorted(segments, key=lambda x: x['score'], reverse=True)
                
                # 计算需要的片段数量
                needed_segments = max(3, int(min_duration / 10))  # 最少选择3个片段
                highlights = sorted_segments[:min(len(sorted_segments), needed_segments)]
                
                # 按时间排序
                highlights.sort(key=lambda x: x['start_time'])
                
                self.logger.info(f"强制选择了 {len(highlights)} 个片段")
        
        return highlights

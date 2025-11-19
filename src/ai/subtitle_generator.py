"""
字幕生成模块
生成SRT格式字幕文件
"""

from typing import List, Dict
from pathlib import Path
from datetime import timedelta
from utils.logger import LoggerMixin


class SubtitleGenerator(LoggerMixin):
    """字幕生成器"""
    
    def __init__(self):
        """初始化字幕生成器"""
        super().__init__()
    
    def _format_time(self, seconds: float) -> str:
        """
        将秒数转换为SRT时间格式
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT时间格式字符串 (HH:MM:SS,mmm)
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_srt(self, segments: List[Dict], output_path: str) -> bool:
        """
        生成SRT字幕文件
        
        Args:
            segments: 字幕片段列表，每个包含start, end, text
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            self.logger.info(f"生成SRT字幕文件: {output_path}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_time(segment['start'])
                    end_time = self._format_time(segment['end'])
                    text = segment['text']
                    
                    # SRT格式：序号、时间范围、文本、空行
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n")
                    f.write("\n")
            
            self.logger.info(f"字幕文件生成成功，共 {len(segments)} 条字幕")
            return True
            
        except Exception as e:
            self.logger.error(f"字幕生成失败: {e}")
            return False
    
    def generate_vtt(self, segments: List[Dict], output_path: str) -> bool:
        """
        生成WebVTT字幕文件
        
        Args:
            segments: 字幕片段列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            self.logger.info(f"生成VTT字幕文件: {output_path}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_time(segment['start']).replace(',', '.')
                    end_time = self._format_time(segment['end']).replace(',', '.')
                    text = segment['text']
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n")
                    f.write("\n")
            
            self.logger.info("VTT字幕文件生成成功")
            return True
            
        except Exception as e:
            self.logger.error(f"VTT字幕生成失败: {e}")
            return False
    
    def adjust_timing(self, segments: List[Dict], offset: float) -> List[Dict]:
        """
        调整字幕时间偏移
        
        Args:
            segments: 字幕片段列表
            offset: 时间偏移量（秒，正数向后，负数向前）
            
        Returns:
            调整后的片段列表
        """
        adjusted = []
        
        for segment in segments:
            adjusted.append({
                'start': max(0, segment['start'] + offset),
                'end': max(0, segment['end'] + offset),
                'text': segment['text']
            })
        
        return adjusted
    
    def merge_short_segments(self, segments: List[Dict], 
                           min_duration: float = 1.0,
                           max_chars: int = 80) -> List[Dict]:
        """
        合并过短的字幕片段
        
        Args:
            segments: 字幕片段列表
            min_duration: 最小时长（秒）
            max_chars: 单条字幕最大字符数
            
        Returns:
            合并后的片段列表
        """
        if not segments:
            return []
        
        merged = []
        current = segments[0].copy()
        
        for next_seg in segments[1:]:
            current_duration = current['end'] - current['start']
            combined_text = current['text'] + ' ' + next_seg['text']
            
            # 如果当前片段太短，且合并后不超过字符限制，则合并
            if current_duration < min_duration and len(combined_text) <= max_chars:
                current['end'] = next_seg['end']
                current['text'] = combined_text
            else:
                merged.append(current)
                current = next_seg.copy()
        
        # 添加最后一个片段
        merged.append(current)
        
        self.logger.info(f"字幕合并完成：{len(segments)} -> {len(merged)} 条")
        return merged

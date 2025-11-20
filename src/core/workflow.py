"""
视频处理工作流引擎
整合所有模块，完成从视频分析到剪辑输出的完整流程
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.video_processor import VideoProcessor
from core.audio_analyzer import AudioAnalyzer
from core.video_analyzer import VideoAnalyzer
from core.highlight_detector import HighlightDetector
from ai.speech_recognition import SpeechRecognizer
from ai.subtitle_generator import SubtitleGenerator
from utils.logger import LoggerMixin
from utils.config import get_config
from utils.database import get_database
from utils.file_manager import FileManager


class VideoProcessingWorkflow(LoggerMixin):
    """视频处理工作流"""
    
    def __init__(self):
        """初始化工作流"""
        super().__init__()
        
        self.config = get_config()
        self.db = get_database()
        self.file_manager = FileManager()
        
        # 初始化处理模块
        self.video_processor = VideoProcessor()
        self.highlight_detector = HighlightDetector(
            audio_weight=self.config.get('highlight.audio_weight', 0.4),
            video_weight=self.config.get('highlight.video_weight', 0.4),
            time_weight=self.config.get('highlight.time_weight', 0.2)
        )
        
        # AI模块（按需加载）
        self.speech_recognizer = None
        self.subtitle_generator = None
        
        self.is_processing = False
        self.should_stop = False
    
    def process_video(self, video_path: str, project_id: int = None) -> Dict:
        """
        处理单个视频文件
        
        Args:
            video_path: 视频文件路径
            project_id: 项目ID
            
        Returns:
            处理结果字典
        """
        self.logger.info(f"开始处理视频: {video_path}")
        start_time = time.time()
        
        try:
            # 1. 验证文件
            valid, error = self.file_manager.validate_file(video_path)
            if not valid:
                return {
                    'success': False, 
                    'error': f'文件验证失败: {error}',
                    'input_path': video_path
                }
            
            # 2. 获取视频信息
            try:
                video_info = self.video_processor.get_video_info(video_path)
            except FileNotFoundError:
                return {
                    'success': False,
                    'error': 'FFmpeg未安装或不在系统PATH中，请先安装FFmpeg',
                    'input_path': video_path
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'读取视频信息失败: {str(e)}',
                    'input_path': video_path
                }
            
            if not video_info:
                return {
                    'success': False, 
                    'error': '无法获取视频信息',
                    'input_path': video_path
                }
            
            self.logger.info(f"视频时长: {video_info['duration']:.2f}秒")
            
            # 3. 高光检测
            min_duration = self.config.get('processing.target_duration_min', 180)
            max_duration = self.config.get('processing.target_duration_max', 300)
            segment_duration = self.config.get('processing.segment_duration', 10)
            
            highlight_result = self.highlight_detector.detect_highlights(
                video_path,
                target_duration_min=min_duration,
                target_duration_max=max_duration,
                segment_duration=segment_duration
            )
            
            if not highlight_result['success']:
                result = highlight_result.copy()
                result['input_path'] = video_path
                return result
            
            # 4. 剪辑视频
            output_dir = self.config.get('output.folder', 'output')
            
            # 确保输出目录存在
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # 生成临时剪辑文件路径
            temp_cut_path = self.file_manager.create_output_path(
                video_path, output_dir, suffix='_temp_cut'
            )
            
            success = self.video_processor.cut_video(
                video_path,
                temp_cut_path,
                highlight_result['time_ranges']
            )
            
            if not success:
                return {
                    'success': False, 
                    'error': '视频剪辑失败',
                    'input_path': video_path
                }
            
            # 5. 处理画面比例（如果需要）
            orientation = self.config.get('processing.orientation', 'original')
            final_output_path = self.file_manager.create_output_path(
                video_path, output_dir, suffix='_edited'
            )
            
            resize_success = True
            if orientation == 'landscape':
                resize_success = self.video_processor.resize_video(
                    temp_cut_path, final_output_path, 1920, 1080
                )
            elif orientation == 'portrait':
                resize_success = self.video_processor.resize_video(
                    temp_cut_path, final_output_path, 1080, 1920
                )
            else:
                # 保持原样，直接重命名
                import shutil
                shutil.move(temp_cut_path, final_output_path)
            
            # 清理临时剪辑文件
            if orientation != 'original' and Path(temp_cut_path).exists():
                Path(temp_cut_path).unlink()
                
            if not resize_success:
                return {
                    'success': False,
                    'error': '视频画面调整失败',
                    'input_path': video_path
                }
            
            # 6. 生成字幕（如果启用）
            subtitle_path = None
            if self.config.get('subtitle.enabled', True):
                subtitle_path = self._generate_subtitles(video_path, final_output_path)
            
            # 7. 记录结果
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'input_path': video_path,
                'output_path': final_output_path,
                'subtitle_path': subtitle_path,
                'processing_time': processing_time,
                'highlights': highlight_result['highlights'],
                'total_duration': highlight_result['total_duration'],
                'segment_count': highlight_result['segment_count']
            }
            
            self.logger.info(f"视频处理完成: {final_output_path}")
            self.logger.info(f"处理时间: {processing_time:.2f}秒")
            
            return result
            
        except Exception as e:
            self.logger.error(f"视频处理失败: {e}", exc_info=True)
            return {
                'success': False, 
                'error': str(e),
                'input_path': video_path
            }
    
    def _generate_subtitles(self, video_path: str, output_video_path: str) -> Optional[str]:
        """
        生成字幕
        
        Args:
            video_path: 原始视频路径
            output_video_path: 输出视频路径
            
        Returns:
            字幕文件路径
        """
        try:
            self.logger.info("开始生成字幕...")
            
            # 提取音频
            temp_audio = Path(output_video_path).parent / "temp_audio_subtitle.wav"
            if not self.video_processor.extract_audio(video_path, str(temp_audio)):
                self.logger.error("音频提取失败")
                return None
            
            # 初始化语音识别（懒加载）
            if not self.speech_recognizer:
                model_size = self.config.get('speech.recognition_model', 'base')
                self.speech_recognizer = SpeechRecognizer(model_size)
            
            # 语音识别
            segments = self.speech_recognizer.get_segments(str(temp_audio), language='zh')
            
            if not segments:
                self.logger.warning("未识别到语音内容")
                temp_audio.unlink()
                return None
            
            # 初始化字幕生成器
            if not self.subtitle_generator:
                self.subtitle_generator = SubtitleGenerator()
            
            # 合并短片段
            segments = self.subtitle_generator.merge_short_segments(segments)
            
            # 生成SRT文件
            subtitle_path = str(Path(output_video_path).with_suffix('.srt'))
            success = self.subtitle_generator.generate_srt(segments, subtitle_path)
            
            # 清理临时文件
            if temp_audio.exists():
                temp_audio.unlink()
            
            if success:
                self.logger.info(f"字幕生成成功: {subtitle_path}")
                return subtitle_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"字幕生成失败: {e}")
            return None
    
    def process_batch(self, video_paths: List[str], 
                     project_id: int = None,
                     callback=None) -> List[Dict]:
        """
        批量处理视频
        
        Args:
            video_paths: 视频文件路径列表
            project_id: 项目ID
            callback: 进度回调函数 callback(current, total, message)
            
        Returns:
            处理结果列表
        """
        self.logger.info(f"开始批量处理 {len(video_paths)} 个视频")
        self.is_processing = True
        self.should_stop = False
        
        results = []
        max_workers = self.config.get('processing.max_workers', 4)
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_path = {
                executor.submit(self.process_video, path, project_id): path
                for path in video_paths
            }
            
            completed = 0
            total = len(video_paths)
            
            # 获取完成的任务
            for future in as_completed(future_to_path):
                if self.should_stop:
                    self.logger.info("批量处理被终止")
                    executor.shutdown(wait=False)
                    break
                
                video_path = future_to_path[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    
                    # 调用回调
                    if callback:
                        if result['success']:
                            message = f"完成: {Path(video_path).name}"
                        else:
                            message = f"失败: {Path(video_path).name} - {result.get('error', '未知错误')}"
                        callback(completed, total, message)
                    
                except Exception as e:
                    self.logger.error(f"处理失败 {video_path}: {e}")
                    results.append({
                        'success': False,
                        'input_path': video_path,
                        'error': str(e)
                    })
        
        self.is_processing = False
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('success', False))
        self.logger.info(f"批量处理完成: {success_count}/{total} 成功")
        
        return results
    
    def stop_processing(self):
        """停止处理"""
        self.logger.info("请求停止处理")
        self.should_stop = True
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.config.get('processing.auto_delete_temp', True):
            self.file_manager.cleanup_temp_files('cache')
            self.file_manager.cleanup_temp_files('temp')

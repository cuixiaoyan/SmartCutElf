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
        self.tts_engine = None

        self.is_processing = False
        self.should_stop = False
    
    def process_video(self, video_path: str, project_id: int = None, video_type: str = None) -> Dict:
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

        # 如果没有project_id，创建一个默认项目
        if project_id is None:
            project_name = f"AutoProject_{time.strftime('%Y%m%d_%H%M%S')}"
            project_id = self.db.create_project(project_name)
            self.logger.info(f"创建自动项目: {project_name} (ID: {project_id})")

        # 添加文件记录到数据库
        video_path_obj = Path(video_path)
        file_size = video_path_obj.stat().st_size if video_path_obj.exists() else 0

        # 获取视频时长用于数据库记录
        try:
            video_info = self.video_processor.get_video_info(video_path)
            duration = video_info.get('duration', 0) if video_info else 0
        except:
            duration = 0

        file_id = self.db.add_file(project_id, video_path, video_path_obj.name, file_size, duration)
        self.db.update_file_status(file_id, 'processing')
        
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

            # 3. 高光检测 - 使用策略模式
            from core.detection_strategies import StrategyFactory, VideoType

            # 将字符串转换为VideoType枚举
            video_type_enum = None
            if video_type:
                try:
                    video_type_enum = VideoType(video_type)
                except ValueError:
                    self.logger.warning(f"未知的视频类型: {video_type}, 使用自动检测")

            # 创建带有策略的检测器
            if video_type_enum:
                strategy = StrategyFactory.create_strategy(video_type_enum)
                self.highlight_detector = HighlightDetector(strategy=strategy)
            else:
                # 使用默认检测器，会在detect_highlights中自动检测类型
                if not hasattr(self, 'highlight_detector') or self.highlight_detector is None:
                    self.highlight_detector = HighlightDetector()

            min_duration = self.config.get('processing.target_duration_min', 180)
            max_duration = self.config.get('processing.target_duration_max', 300)
            segment_duration = self.config.get('processing.segment_duration', 10)

            highlight_result = self.highlight_detector.detect_highlights(
                video_path,
                target_duration_min=min_duration,
                target_duration_max=max_duration,
                segment_duration=segment_duration,
                video_type=video_type_enum
            )
            
            if not highlight_result['success']:
                result = highlight_result.copy()
                result['input_path'] = video_path
                return result
            
            # 验证高光检测结果的有效性
            time_ranges = highlight_result.get('time_ranges', [])
            if not time_ranges:
                return {
                    'success': False,
                    'error': '高光检测未返回有效的时间段',
                    'input_path': video_path
                }
            
            # 验证时间段的合理性
            for i, (start, end) in enumerate(time_ranges):
                if start >= end or start < 0:
                    return {
                        'success': False,
                        'error': f'无效的时间段 {i+1}: {start}-{end}秒',
                        'input_path': video_path
                    }
            
            self.logger.info(f"高光检测成功，共 {len(time_ranges)} 个片段，总时长: {highlight_result['total_duration']:.2f}秒")
            
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
            
            # 验证临时文件是否存在
            if not Path(temp_cut_path).exists():
                return {
                    'success': False,
                    'error': f'临时剪辑文件不存在: {temp_cut_path}',
                    'input_path': video_path
                }
            
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
                try:
                    shutil.move(temp_cut_path, final_output_path)
                except Exception as e:
                    self.logger.error(f"移动文件失败: {e}")
                    return {
                        'success': False,
                        'error': f'移动文件失败: {str(e)}',
                        'input_path': video_path
                    }
            
            # 清理临时剪辑文件
            if orientation != 'original' and Path(temp_cut_path).exists():
                try:
                    Path(temp_cut_path).unlink()
                except Exception as e:
                    self.logger.warning(f"清理临时文件失败: {e}")
                
            if not resize_success:
                return {
                    'success': False,
                    'error': '视频画面调整失败',
                    'input_path': video_path
                }
            
            # 6. 生成字幕（如果启用）
            subtitle_path = None
            subtitle_segments = None
            if self.config.get('subtitle.enabled', True):
                subtitle_result = self._generate_subtitles(video_path, final_output_path)
                if subtitle_result:
                    subtitle_path = subtitle_result.get('path')
                    subtitle_segments = subtitle_result.get('segments')

            # 6.5 生成配音（如果启用）
            tts_audio_path = None
            if self.config.get('speech.tts_enabled', False) and subtitle_segments:
                tts_audio_path = self._generate_tts_audio(subtitle_segments, final_output_path)

            # 如果生成了配音，混入原视频
            if tts_audio_path:
                final_output_with_tts = str(Path(final_output_path).parent / Path(final_output_path).stem.replace('_edited', '_tts')) + '.mp4'
                if self._mix_audio_to_video(final_output_path, tts_audio_path, final_output_with_tts):
                    # 替换原输出文件
                    import shutil
                    shutil.move(final_output_with_tts, final_output_path)
                    self.logger.info(f"TTS配音已混入视频: {final_output_path}")

            # 7. 记录结果到数据库
            processing_time = time.time() - start_time

            # 保存处理结果到数据库
            self.db.save_processing_result(
                file_id=file_id,
                output_path=final_output_path,
                processing_time=processing_time,
                highlights=highlight_result['highlights'],
                subtitles=[{'path': subtitle_path}] if subtitle_path else None
            )
            self.db.update_file_status(file_id, 'completed')

            result = {
                'success': True,
                'input_path': video_path,
                'output_path': final_output_path,
                'subtitle_path': subtitle_path,
                'processing_time': processing_time,
                'highlights': highlight_result['highlights'],
                'total_duration': highlight_result['total_duration'],
                'segment_count': highlight_result['segment_count'],
                'file_id': file_id,
                'project_id': project_id
            }

            self.logger.info(f"视频处理完成: {final_output_path}")
            self.logger.info(f"处理时间: {processing_time:.2f}秒")

            return result

        except Exception as e:
            self.logger.error(f"视频处理失败: {e}", exc_info=True)

            # 记录错误到数据库
            if 'file_id' in locals():
                self.db.update_file_status(file_id, 'failed')
                self.db.log_error(
                    file_id=file_id,
                    error_type='processing_error',
                    error_message=str(e),
                    stack_trace=None
                )

            return {
                'success': False,
                'error': str(e),
                'input_path': video_path
            }
    
    def _generate_subtitles(self, video_path: str, output_video_path: str) -> Optional[Dict]:
        """
        生成字幕

        Args:
            video_path: 原始视频路径
            output_video_path: 输出视频路径

        Returns:
            字幕信息字典 {'path': subtitle_path, 'segments': segments} 或 None
        """
        try:
            self.logger.info("开始生成字幕...")

            output_video_info = self.video_processor.get_video_info(output_video_path)
            if not output_video_info:
                self.logger.warning(f"无法读取输出视频信息，跳过字幕生成: {output_video_path}")
                return None
            if not output_video_info.get('audio_codec'):
                self.logger.info(f"输出视频没有音轨，跳过字幕生成: {output_video_path}")
                return None

            # 提取音频 (从输出视频提取，以匹配剪辑后的时间轴)
            temp_audio = Path(output_video_path).parent / "temp_audio_subtitle.wav"
            # 注意：这里应该使用 output_video_path 而不是 video_path
            if not self.video_processor.extract_audio(output_video_path, str(temp_audio)):
                self.logger.warning("字幕生成阶段音频提取失败，已跳过")
                return None

            # 检查音频文件大小
            if temp_audio.stat().st_size < 1024:
                self.logger.warning(f"提取的音频文件过小 ({temp_audio.stat().st_size} bytes)，可能没有声音")
                temp_audio.unlink()
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
                from ai.subtitle_generator import SubtitleGenerator
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
                return {
                    'path': subtitle_path,
                    'segments': segments
                }

            return None

        except Exception as e:
            self.logger.error(f"字幕生成失败: {e}")
            return None

    def _generate_tts_audio(self, subtitle_segments: List[Dict], output_video_path: str) -> Optional[str]:
        """
        生成TTS配音

        Args:
            subtitle_segments: 字幕片段列表
            output_video_path: 输出视频路径

        Returns:
            TTS音频文件路径或None
        """
        try:
            from ai.text_to_speech import TextToSpeech
            from pathlib import Path

            self.logger.info("开始生成TTS配音...")

            # 初始化TTS引擎
            if not self.tts_engine:
                tts_config = {
                    'rate': 150,
                    'volume': 0.9,
                    'voice': self.config.get('speech.tts_voice', 'female')
                }
                self.tts_engine = TextToSpeech(tts_config)

            # 生成TTS音频输出路径
            tts_audio_path = str(Path(output_video_path).parent / "tts_audio.wav")

            # 从字幕片段生成配音
            full_text = " ".join([seg.get('text', '') for seg in subtitle_segments if seg.get('text')])

            if not full_text:
                self.logger.warning("没有有效的文本内容用于TTS")
                return None

            # 生成语音
            if self.tts_engine.synthesize(full_text, tts_audio_path):
                self.logger.info(f"TTS配音生成成功: {tts_audio_path}")
                return tts_audio_path
            else:
                self.logger.error("TTS配音生成失败")
                return None

        except Exception as e:
            self.logger.error(f"TTS配音生成异常: {e}")
            return None

    def _mix_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        将音频混入视频

        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        try:
            import subprocess
            import sys

            # Windows上隐藏subprocess控制台窗口
            if sys.platform == 'win32':
                CREATE_NO_WINDOW = 0x08000000
            else:
                CREATE_NO_WINDOW = 0

            # 获取BGM音量设置
            bgm_volume = self.config.get('speech.music_volume', 30) / 100.0

            # FFmpeg命令: 混合原音频和TTS音频
            cmd = [
                self.video_processor.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-filter_complex',
                f'[0:a][1:a]amix=inputs=2:duration=first:weights=1 {bgm_volume}[aout]',
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-y',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, encoding='utf-8',
                                  errors='ignore', creationflags=CREATE_NO_WINDOW)

            if result.returncode != 0:
                self.logger.error(f"音频混合失败: {result.stderr[-200:]}")
                return False

            self.logger.info(f"音频混合成功: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"音频混合异常: {e}")
            return False
    
    def process_batch(self, video_paths: List[str],
                     project_id: int = None,
                     video_type: str = None,
                     callback=None) -> List[Dict]:
        """
        批量处理视频

        Args:
            video_paths: 视频文件路径列表
            project_id: 项目ID
            video_type: 视频类型 (None=自动检测)
            callback: 进度回调函数 callback(current, total, message)

        Returns:
            处理结果列表
        """
        self.logger.info(f"开始批量处理 {len(video_paths)} 个视频")
        if video_type:
            self.logger.info(f"指定视频类型: {video_type}")
        self.is_processing = True
        self.should_stop = False

        results = []
        max_workers = self.config.get('processing.max_workers', 4)
        total = len(video_paths)

        if project_id is None and video_paths:
            project_name = f"BatchProject_{time.strftime('%Y%m%d_%H%M%S')}_{total}files"
            project_id = self.db.create_project(project_name)
            self.logger.info(f"创建批处理项目: {project_name} (ID: {project_id})")

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_path = {
                executor.submit(self.process_video, path, project_id, video_type): path
                for path in video_paths
            }
            
            completed = 0
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

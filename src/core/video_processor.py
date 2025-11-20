"""
视频处理引擎
使用FFmpeg进行视频处理
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from utils.logger import LoggerMixin


class VideoProcessor(LoggerMixin):
    """视频处理器"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        """
        初始化视频处理器
        
        Args:
            ffmpeg_path: FFmpeg可执行文件路径
            ffprobe_path: FFprobe可执行文件路径
        """
        super().__init__()
        
        # 尝试查找FFmpeg
        self.ffmpeg_path = self._find_ffmpeg(ffmpeg_path)
        self.ffprobe_path = self._find_ffmpeg(ffprobe_path)
    
    def _find_ffmpeg(self, default_name: str) -> str:
        """查找FFmpeg可执行文件"""
        import shutil
        
        # 首先尝试在PATH中查找
        found = shutil.which(default_name)
        if found:
            return default_name
        
        # 尝试常见的安装路径
        common_paths = [
            r"D:\ffmpeg-master-latest-win64-gpl-shared\bin",
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
        ]
        
        for path in common_paths:
            exe_path = Path(path) / f"{default_name}.exe"
            if exe_path.exists():
                self.logger.info(f"找到FFmpeg: {exe_path}")
                return str(exe_path)
        
        # 如果都找不到，返回默认值（会在后续抛出错误）
        return default_name
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        获取视频详细信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            # 修复Windows编码问题
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='ignore',  # 忽略无法解码的字符
                check=True
            )
            data = json.loads(result.stdout)
            
            # 提取视频流信息
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            format_info = data.get('format', {})
            
            info = {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'format_name': format_info.get('format_name', 'unknown'),
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': self._parse_fps(video_stream.get('r_frame_rate', '0/1')),
                    'video_codec': video_stream.get('codec_name', 'unknown'),
                    'video_bitrate': int(video_stream.get('bit_rate', 0))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', 'unknown'),
                    'audio_sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'audio_channels': int(audio_stream.get('channels', 0)),
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0))
                })
            
            self.logger.debug(f"视频信息: {video_path} - {info.get('duration')}秒")
            return info
            
        except Exception as e:
            self.logger.error(f"获取视频信息失败: {e}")
            return None
    
    def _parse_fps(self, fps_str: str) -> float:
        """解析帧率字符串"""
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                return float(num) / float(den)
            return float(fps_str)
        except:
            return 0.0
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径
            
        Returns:
            是否成功
        """
        try:
            # 验证输入文件
            if not Path(video_path).exists():
                self.logger.error(f"视频文件不存在: {video_path}")
                return False
            
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vn',  # 不包含视频
                '-acodec', 'pcm_s16le',  # PCM格式
                '-ar', '16000',  # 采样率16kHz（Whisper推荐）
                '-ac', '1',  # 单声道
                '-y',  # 覆盖输出文件
                output_path
            ]
            
            self.logger.debug(f"音频提取命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                error_msg = f"音频提取失败 (returncode: {result.returncode})\n"
                error_msg += f"stderr: {result.stderr}\n"
                error_msg += f"stdout: {result.stdout}"
                self.logger.error(error_msg)
                return False
            
            # 验证输出文件
            if not Path(output_path).exists():
                self.logger.error(f"音频文件未创建: {output_path}")
                return False
            
            file_size = Path(output_path).stat().st_size
            if file_size == 0:
                self.logger.error(f"音频文件为空: {output_path}")
                return False
            
            self.logger.info(f"音频提取成功: {output_path} ({file_size/1024:.1f}KB)")
            return True
            
        except Exception as e:
            self.logger.error(f"音频提取异常: {e}")
            return False
    
    def cut_video(self, video_path: str, output_path: str, 
                  segments: List[Tuple[float, float]]) -> bool:
        """
        根据时间片段剪辑视频
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            segments: 时间段列表 [(start1, end1), (start2, end2), ...]
            
        Returns:
            是否成功
        """
        if not segments:
            self.logger.error("没有提供剪辑片段")
            return False
        
        import shutil
        import time
        
        temp_dir = None
        try:
            # 验证FFmpeg可用性
            try:
                test_result = subprocess.run([self.ffmpeg_path, '-version'], 
                                           capture_output=True, timeout=10)
                if test_result.returncode != 0:
                    raise Exception(f"FFmpeg不可用: {self.ffmpeg_path}")
            except Exception as e:
                raise Exception(f"FFmpeg检查失败: {e}")
            
            # 验证时间段有效性
            for i, (start, end) in enumerate(segments):
                if start < 0 or end <= start:
                    raise Exception(f"无效的时间段 {i+1}: {start:.2f}-{end:.2f}秒")
                if end - start < 0.5:
                    self.logger.warning(f"时间段 {i+1} 过短: {end-start:.2f}秒")
            
            self.logger.info(f"开始剪切 {len(segments)} 个片段")
            
            # 创建临时分段文件列表
            # 使用Windows TEMP目录避免中文路径问题（FFmpeg在Windows上无法正确处理Unicode路径）
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix="smartcut_segments_"))
            self.logger.info(f"临时目录已创建: {temp_dir}")
            
            segment_files = []
            failed_segments = []
            successful_count = 0
            
            # 剪切每个片段
            for i, (start, end) in enumerate(segments):
                # 使用原始索引作为临时文件名
                temp_segment_file = temp_dir / f"temp_segment_{i:04d}.mp4"
                duration = end - start
                
                # 使用重新编码而不是复制编码，避免关键帧问题导致的白屏
                # -ss 放在 -i 之前可以更快，但可能不精确
                # -ss 放在 -i 之后更精确，但稍慢
                # 构建 FFmpeg 命令
                cmd = [
                    self.ffmpeg_path,
                    '-ss', f"{start:.3f}",  # 精确到毫秒
                    '-i', video_path,
                    '-t', f"{duration:.3f}",  # 精确的持续时间
                    '-c:v', 'libx264',  # 重新编码视频
                    '-preset', 'fast',  # 快速编码
                    '-crf', '23',  # 质量控制
                    '-c:a', 'aac',  # 音频编码
                    '-b:a', '192k',  # 音频比特率
                    '-movflags', '+faststart',  # 优化网络播放
                    '-avoid_negative_ts', 'make_zero',  # 处理负时间戳
                    '-y',  # 覆盖输出文件
                    str(temp_segment_file)
                ]
                
                self.logger.debug(f"正在剪切片段 {i+1}/{len(segments)}: {start:.2f}-{end:.2f}s ({duration:.2f}s)")
                self.logger.debug(f"FFmpeg命令: {' '.join(cmd)}")
                
                try:
                    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', 
                                          errors='replace', timeout=300)  # 5分钟超时
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"片段 {i+1} 剪切超时，跳过")
                    failed_segments.append({
                        'index': i,
                        'start': start,
                        'end': end,
                        'error': 'Timeout'
                    })
                    continue
                
                if result.returncode != 0:
                    # 尝试使用备用策略
                    self.logger.warning(f"片段 {i+1} 标准剪切失败，尝试备用策略")
                    
                    # 备用命令：使用复制模式，更保守的参数
                    backup_cmd = [
                        self.ffmpeg_path,
                        '-ss', f"{start:.3f}",
                        '-i', video_path,
                        '-t', f"{duration:.3f}",
                        '-c', 'copy',  # 复制模式，不重新编码
                        '-avoid_negative_ts', 'make_zero',
                        '-y',
                        str(temp_segment_file)
                    ]
                    
                    self.logger.debug(f"备用FFmpeg命令: {' '.join(backup_cmd)}")
                    
                    try:
                        backup_result = subprocess.run(backup_cmd, capture_output=True, 
                                                     encoding='utf-8', errors='replace', timeout=300)
                        
                        if backup_result.returncode != 0:
                            # 两种方法都失败，记录并跳过
                            # 提取真正的错误信息（跳过版本信息）
                            stderr_lines = result.stderr.split('\n') if result.stderr else []
                            error_lines = [line for line in stderr_lines if line and not line.startswith('ffmpeg version') and not line.startswith('  built') and not line.startswith('  configuration')]
                            actual_error = '\n'.join(error_lines[-5:]) if error_lines else 'No error message'
                            
                            error_msg = f"片段 {i+1} 剪切失败 (标准和备用方法都失败)\n"
                            error_msg += f"时间段: {start:.2f}-{end:.2f}s (时长: {duration:.2f}s)\n"
                            error_msg += f"错误: {actual_error}"
                            self.logger.warning(error_msg)
                            
                            failed_segments.append({
                                'index': i,
                                'start': start,
                                'end': end,
                                'error': result.stderr[:100] if result.stderr else 'Unknown'
                            })
                            
                            # 跳过这个片段，继续下一个
                            self.logger.info(f"跳过片段 {i+1}，继续处理下一个")
                            continue
                        else:
                            self.logger.info(f"片段 {i+1} 备用策略成功")
                    
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"片段 {i+1} 备用剪切超时，跳过")
                        failed_segments.append({
                            'index': i,
                            'start': start,
                            'end': end,
                            'error': 'Timeout'
                        })
                        continue
                
                # 等待文件系统完成写入
                time.sleep(0.3)
                
                # 验证文件是否创建成功
                max_wait = 10  # 最多等待10秒
                wait_count = 0
                while not temp_segment_file.exists() and wait_count < max_wait:
                    time.sleep(0.5)
                    wait_count += 1
                
                if not temp_segment_file.exists():
                    self.logger.warning(f"片段文件未创建: {temp_segment_file}，跳过")
                    failed_segments.append({
                        'index': i,
                        'start': start,
                        'end': end,
                        'error': 'File not created'
                    })
                    continue
                
                file_size = temp_segment_file.stat().st_size
                if file_size == 0:
                    self.logger.warning(f"片段文件为空: {temp_segment_file}，跳过")
                    failed_segments.append({
                        'index': i,
                        'start': start,
                        'end': end,
                        'error': 'Empty file'
                    })
                    # 删除空文件
                    try:
                        temp_segment_file.unlink()
                    except:
                        pass
                    continue
                
                # 重命名为连续编号
                final_segment_file = temp_dir / f"segment_{successful_count:04d}.mp4"
                self.logger.debug(f"准备重命名: {temp_segment_file.name} -> {final_segment_file.name} (successful_count={successful_count})")
                try:
                    # 如果目标文件已存在，先删除
                    if final_segment_file.exists():
                        final_segment_file.unlink()
                    
                    shutil.move(str(temp_segment_file), str(final_segment_file))
                    self.logger.debug(f"重命名成功: {temp_segment_file.name} -> {final_segment_file.name}")
                    
                    # 验证重命名成功
                    if not final_segment_file.exists():
                        raise Exception("重命名后文件不存在")
                    
                except Exception as e:
                    self.logger.error(f"重命名失败: {e}")
                    # 如果重命名失败，跳过这个片段
                    failed_segments.append({
                        'index': i,
                        'start': start,
                        'end': end,
                        'error': f'Rename failed: {e}'
                    })
                    continue
                
                segment_files.append(final_segment_file)
                successful_count += 1
                self.logger.info(f"片段 {i+1}/{len(segments)} 剪切成功: {final_segment_file.name}, {file_size/1024/1024:.2f}MB (成功: {successful_count})")
            
            # 检查是否有足够的成功片段
            if not segment_files:
                error_msg = f"所有片段都剪切失败，无法继续\n"
                error_msg += f"失败片段数: {len(failed_segments)}\n"
                for fail in failed_segments[:3]:  # 只显示前3个
                    error_msg += f"  - 片段 {fail['index']+1}: {fail['start']:.1f}-{fail['end']:.1f}s, 错误: {fail['error']}\n"
                raise Exception(error_msg)
            
            if failed_segments:
                self.logger.warning(
                    f"有 {len(failed_segments)} 个片段失败，但有 {len(segment_files)} 个成功，继续合并"
                )
                # 显示成功的文件列表
                self.logger.info(f"成功的片段: {[f.name for f in segment_files]}")
            
            # 再次等待确保所有文件句柄已释放
            time.sleep(0.2)
            
            # 合并所有成功的片段
            if len(segment_files) == 1:
                # 只有一个片段，直接移动
                shutil.move(str(segment_files[0]), output_path)
            else:
                # 多个片段，需要合并
                if not self._concat_videos(segment_files, output_path):
                    raise Exception("视频合并失败")
            
            # 验证输出文件
            if not Path(output_path).exists():
                raise Exception(f"输出文件未创建: {output_path}")
            
            self.logger.info(f"视频剪辑完成: {output_path}")
            return True
            
        except Exception as e:
            error_msg = f"视频剪辑失败: {e}"
            if temp_dir and temp_dir.exists():
                # 显示临时目录中的文件
                try:
                    files = list(temp_dir.glob("*"))
                    error_msg += f"\n临时目录文件: {[f.name for f in files]}"
                    # 显示文件大小
                    for f in files:
                        if f.is_file():
                            error_msg += f"\n  - {f.name}: {f.stat().st_size} bytes"
                except Exception as list_error:
                    error_msg += f"\n无法列出文件: {list_error}"
            self.logger.error(error_msg)
            return False
        finally:
            # 清理临时文件（无论成功或失败）
            if temp_dir and temp_dir.exists():
                try:
                    time.sleep(0.3)  # 等待文件句柄释放
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    self.logger.warning(f"清理临时文件失败: {cleanup_error}")
    
    def _concat_videos(self, video_files: List[Path], output_path: str, reencode: bool = False) -> bool:
        """
        合并多个视频文件
        
        Args:
            video_files: 视频文件路径列表
            output_path: 输出文件路径
            reencode: 是否重新编码（True更安全但更慢，False更快但可能有兼容性问题）
            
        Returns:
            是否成功
        """
        concat_file = None
        try:
            # 验证所有输入文件存在
            for video_file in video_files:
                if not video_file.exists():
                    self.logger.error(f"视频文件不存在: {video_file}")
                    return False
                if video_file.stat().st_size == 0:
                    self.logger.error(f"视频文件为空: {video_file}")
                    return False
            
            # 创建文件列表
            concat_file = Path(output_path).parent / "concat_list.txt"
            
            with open(concat_file, 'w', encoding='utf-8') as f:
                for video_file in video_files:
                    # FFmpeg concat需要使用绝对路径，并且路径中的反斜杠需要转义
                    abs_path = str(video_file.absolute()).replace('\\', '/')
                    # 对路径中的单引号进行转义，避免FFmpeg解析错误
                    escaped_path = abs_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            # 验证concat文件创建成功
            if not concat_file.exists():
                self.logger.error("concat列表文件创建失败")
                return False
            
            if reencode:
                # 重新编码模式 - 更安全，确保兼容性
                cmd = [
                    self.ffmpeg_path,
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-movflags', '+faststart',
                    '-y',
                    output_path
                ]
            else:
                # 复制模式 - 更快
                cmd = [
                    self.ffmpeg_path,
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c', 'copy',
                    '-y',
                    output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                self.logger.error(f"视频合并失败: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"视频合并异常: {e}")
            return False
        finally:
            # 清理concat列表文件
            if concat_file and concat_file.exists():
                try:
                    concat_file.unlink()
                except Exception as e:
                    self.logger.warning(f"删除concat列表文件失败: {e}")
    
    def add_subtitles(self, video_path: str, subtitle_path: str, 
                     output_path: str) -> bool:
        """
        为视频添加字幕
        
        Args:
            video_path: 视频文件路径
            subtitle_path: 字幕文件路径（SRT格式）
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', f"subtitles={subtitle_path}",
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"字幕添加成功: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"字幕添加失败: {e.stderr}")
            return False

    def resize_video(self, input_path: str, output_path: str, 
                    target_width: int = 1920, target_height: int = 1080) -> bool:
        """
        调整视频大小和比例（支持裁剪填充）
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            target_width: 目标宽度
            target_height: 目标高度
            
        Returns:
            是否成功
        """
        try:
            # 使用scale和pad过滤器保持比例并填充背景
            filter_complex = (
                f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black"
            )
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', filter_complex,
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', check=True)
            self.logger.info(f"视频尺寸调整成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"视频尺寸调整失败: {e}")
            return False

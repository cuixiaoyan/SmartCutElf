"""
视频处理引擎
使用FFmpeg进行视频处理
"""

import subprocess
import json
import sys
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from utils.logger import LoggerMixin
from utils.config import get_config
from utils.ffmpeg_pool import get_ffmpeg_pool

# Windows上隐藏subprocess控制台窗口
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


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
        self.config = get_config()
        
        # 尝试查找FFmpeg
        self.ffmpeg_path = self._find_ffmpeg(ffmpeg_path)
        self.ffprobe_path = self._find_ffmpeg(ffprobe_path)
        
        # 检查GPU支持
        self.gpu_enabled = False
        self.encoder_name = "libx264"
        self._check_gpu()
    
    def _find_ffmpeg(self, default_name: str) -> str:
        """查找FFmpeg可执行文件"""
        
        # 1. 尝试配置中的路径 (如果有)
        config_path = self.config.get(f'paths.{default_name}')
        if config_path and Path(config_path).exists():
            return config_path

        # 2. 尝试在PATH中查找
        found = shutil.which(default_name)
        if found:
            return default_name
        
        # 3. 尝试当前目录下的 bin 目录
        local_bin = Path.cwd() / 'bin' / f"{default_name}.exe"
        if local_bin.exists():
            return str(local_bin)
            
        # 4. 尝试常见的安装路径
        common_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"D:\ffmpeg\bin",
        ]
        
        for path in common_paths:
            exe_path = Path(path) / f"{default_name}.exe"
            if exe_path.exists():
                self.logger.info(f"找到FFmpeg: {exe_path}")
                return str(exe_path)
        
        # 如果都找不到，返回默认值
        return default_name

    def _check_gpu(self):
        """检查GPU加速可用性"""
        try:
            # 获取用户配置的编码器
            config_codec = self.config.get('output.video_codec', 'libx264')
            
            # 如果是CPU编码器，直接使用
            if config_codec == 'libx264':
                self.encoder_name = 'libx264'
                self.gpu_enabled = False
                return

            # 检查硬件编码器是否可用
            cmd = [self.ffmpeg_path, '-encoders']
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            
            if config_codec in result.stdout:
                self.encoder_name = config_codec
                self.gpu_enabled = True
                self.logger.info(f"启用GPU加速: {self.encoder_name}")
            else:
                self.logger.warning(f"未找到编码器 {config_codec}，回退到 libx264")
                self.encoder_name = 'libx264'
                self.gpu_enabled = False
                
        except Exception as e:
            self.logger.warning(f"检查GPU失败: {e}，使用CPU编码")
            self.encoder_name = 'libx264'
            self.gpu_enabled = False

    def _get_encoding_args(self, reencode: bool = True) -> List[str]:
        """获取编码参数"""
        if not reencode:
            return ['-c', 'copy']
            
        args = ['-c:v', self.encoder_name]
        
        # 根据编码器设置参数
        preset = self.config.get('output.preset', 'medium')
        
        if self.gpu_enabled:
            # NVIDIA GPU 参数
            if 'nvenc' in self.encoder_name:
                args.extend(['-preset', preset]) # p1-p7 for newer nvenc, but preset names usually work too
                # constant quality mode for nvenc
                crf = self.config.get('output.crf', 23)
                args.extend(['-rc', 'vbr', '-cq', str(crf), '-qmin', str(crf), '-qmax', str(crf)])
            # Intel QSV
            elif 'qsv' in self.encoder_name:
                args.extend(['-global_quality', str(self.config.get('output.crf', 23))])
        else:
            # CPU x264
            args.extend(['-preset', preset])
            args.extend(['-crf', str(self.config.get('output.crf', 23))])
            
        # 音频参数
        args.extend(['-c:a', 'aac', '-b:a', '192k'])
        
        return args
    
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
                creationflags=CREATE_NO_WINDOW,  # 隐藏控制台窗口
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
            
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', creationflags=CREATE_NO_WINDOW)
            
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
        根据时间片段剪辑视频 (并行处理)
        
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
        
        import tempfile
        import shutil
        
        temp_dir = None
        try:
            # 验证FFmpeg可用性
            try:
                subprocess.run([self.ffmpeg_path, '-version'], 
                             capture_output=True, timeout=10, creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                raise Exception(f"FFmpeg检查失败: {e}")
            
            self.logger.info(f"开始剪切 {len(segments)} 个片段 (并行处理)")
            
            # 创建临时目录
            temp_dir = Path(tempfile.mkdtemp(prefix="smartcut_segments_"))
            self.logger.info(f"临时目录已创建: {temp_dir}")
            
            # 准备任务参数
            tasks = []
            for i, (start, end) in enumerate(segments):
                task_args = {
                    'index': i,
                    'start': start,
                    'end': end,
                    'video_path': video_path,
                    'temp_dir': temp_dir,
                    'ffmpeg_path': self.ffmpeg_path
                }
                tasks.append(task_args)
            
            # 获取并行配置
            max_workers = self.config.get('processing.max_segment_workers', 4)
            pool = get_ffmpeg_pool(max_workers=max_workers)
            
            # 并行执行任务
            self.logger.info(f"提交 {len(tasks)} 个剪切任务 (并发数: {max_workers})")
            results = pool.map_tasks(self._cut_segment_task, tasks)
            
            # 处理结果
            segment_files = []
            failed_segments = []
            
            for res in results:
                if res and res.get('success'):
                    segment_files.append(res['file_path'])
                else:
                    if res:
                        failed_segments.append(res)
                    else:
                        failed_segments.append({'error': 'Unknown error'})
            
            # 检查结果
            if not segment_files:
                raise Exception(f"所有片段都剪切失败 (失败数: {len(failed_segments)})")
            
            if failed_segments:
                self.logger.warning(f"有 {len(failed_segments)} 个片段失败，但有 {len(segment_files)} 个成功，继续合并")
                
            # 按索引排序确保顺序正确 (虽然map_tasks通常保持顺序，但为了安全起见)
            segment_files.sort(key=lambda p: int(p.stem.split('_')[-1]))
            
            # 合并片段
            self.logger.info(f"开始合并 {len(segment_files)} 个片段...")
            succ = self._concat_videos(segment_files, output_path, reencode=True) # 使用reencode以确保衔接平滑和应用统一编码
            
            if succ:
                self.logger.info(f"视频剪辑完成: {output_path}")
                return True
            else:
                raise Exception("视频合并失败")
                
        except Exception as e:
            self.logger.error(f"视频剪辑失败: {e}")
            return False
        finally:
            # 清理临时文件
            if temp_dir and temp_dir.exists():
                try:
                    # 在Windows上可能需要稍等一下让文件句柄释放
                    time.sleep(0.5)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    self.logger.warning(f"清理临时文件失败: {cleanup_error}")

    def _cut_segment_task(self, args: Dict) -> Dict:
        """
        单个片段剪切任务 (用于并行执行)
        
        Args:
            args: 包含 index, start, end, video_path, temp_dir, ffmpeg_path 的字典
            
        Returns:
            结果字典
        """
        try:
            index = args['index']
            start = args['start']
            end = args['end']
            video_path = args['video_path']
            temp_dir = args['temp_dir']
            ffmpeg_path = args['ffmpeg_path']
            
            duration = end - start
            if duration < 0.1:
                return {'success': False, 'error': 'Duration too short', 'index': index}
                
            output_file = temp_dir / f"segment_{index:04d}.mp4"
            
            # 构建命令
            # 使用快速剪切重新编码模式
            # 注意: 这里虽然是多线程，但每个FFmpeg进程是独立的
            cmd = [
                ffmpeg_path,
                '-ss', f"{start:.3f}",
                '-i', video_path,
                '-t', f"{duration:.3f}",
            ]
            
            # 获取编码参数
            encoding_args = self._get_encoding_args(reencode=True)
            cmd.extend(encoding_args)
            
            cmd.extend([
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                '-y',
                str(output_file)
            ])
            
            # 执行命令
            # 每个子进程不需要太长的超时，因为片段通常较短
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', 
                                  errors='replace', timeout=300, creationflags=CREATE_NO_WINDOW)
            
            if result.returncode != 0:
                return {
                    'success': False, 
                    'error': f"FFmpeg error: {result.stderr[-200:]}", 
                    'index': index
                }
                
            if not output_file.exists() or output_file.stat().st_size == 0:
                return {
                    'success': False, 
                    'error': "Output file empty or missing", 
                    'index': index
                }
                
            return {
                'success': True,
                'file_path': output_file,
                'index': index
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': str(e), 
                'index': args.get('index', -1)
            }

    
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
                ]
                
                # 获取编码参数
                cmd.extend(self._get_encoding_args(reencode=True))
                
                cmd.extend([
                    '-movflags', '+faststart',
                    '-y',
                    output_path
                ])
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
            
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', creationflags=CREATE_NO_WINDOW)
            
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
            
            subprocess.run(cmd, capture_output=True, check=True, creationflags=CREATE_NO_WINDOW)
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
            ]
            
            # 使用统一的编码参数
            cmd.extend(self._get_encoding_args(reencode=True))
            
            cmd.extend([
                '-y',
                output_path
            ])
            
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', check=True, creationflags=CREATE_NO_WINDOW)
            self.logger.info(f"视频尺寸调整成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"视频尺寸调整失败: {e}")
            return False


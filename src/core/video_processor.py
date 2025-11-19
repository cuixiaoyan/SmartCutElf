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
            
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', check=True)
            self.logger.info(f"音频提取成功: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"音频提取失败: {e.stderr}")
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
        
        try:
            # 创建临时分段文件列表
            temp_dir = Path(output_path).parent / "temp_segments"
            temp_dir.mkdir(exist_ok=True)
            
            segment_files = []
            
            # 剪切每个片段
            for i, (start, end) in enumerate(segments):
                segment_file = temp_dir / f"segment_{i:04d}.mp4"
                
                cmd = [
                    self.ffmpeg_path,
                    '-i', video_path,
                    '-ss', str(start),
                    '-to', str(end),
                    '-c', 'copy',  # 复制编码，快速剪辑
                    '-y',
                    str(segment_file)
                ]
                
                subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', check=True)
                segment_files.append(segment_file)
                self.logger.debug(f"片段 {i+1}/{len(segments)} 剪切完成")
            
            # 合并所有片段
            if len(segment_files) == 1:
                # 只有一个片段，直接移动
                import shutil
                shutil.move(str(segment_files[0]), output_path)
            else:
                # 多个片段，需要合并
                self._concat_videos(segment_files, output_path)
            
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir)
            
            self.logger.info(f"视频剪辑完成: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"视频剪辑失败: {e}")
            return False
    
    def _concat_videos(self, video_files: List[Path], output_path: str) -> bool:
        """
        合并多个视频文件
        
        Args:
            video_files: 视频文件路径列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        # 创建文件列表
        concat_file = Path(output_path).parent / "concat_list.txt"
        
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                # FFmpeg concat需要使用相对路径或绝对路径
                f.write(f"file '{video_file.absolute()}'\n")
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', check=True)
            concat_file.unlink()  # 删除临时文件列表
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"视频合并失败: {e.stderr}")
            if concat_file.exists():
                concat_file.unlink()
            return False
    
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
    
    def resize_video(self, video_path: str, output_path: str, 
                    width: int, height: int) -> bool:
        """
        调整视频分辨率
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            width: 目标宽度
            height: 目标高度
            
        Returns:
            是否成功
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', f'scale={width}:{height}',
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"视频调整成功: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"视频调整失败: {e.stderr}")
            return False

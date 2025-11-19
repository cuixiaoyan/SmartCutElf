"""
音频分析模块
分析音频特征，检测音量变化、静音段等
"""

import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_silence
from typing import List, Dict, Tuple
from utils.logger import LoggerMixin


class AudioAnalyzer(LoggerMixin):
    """音频分析器"""
    
    def __init__(self):
        """初始化音频分析器"""
        super().__init__()
    
    def load_audio(self, audio_path: str) -> AudioSegment:
        """
        加载音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            AudioSegment对象
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            self.logger.debug(f"音频加载成功: {audio_path}")
            return audio
        except Exception as e:
            self.logger.error(f"音频加载失败: {e}")
            raise
    
    def detect_volume_changes(self, audio: AudioSegment, 
                            window_size: float = 1.0,
                            threshold: float = 0.3) -> List[Dict]:
        """
        检测音量变化点
        
        Args:
            audio: 音频对象
            window_size: 窗口大小（秒）
            threshold: 变化阈值（0-1）
            
        Returns:
            音量变化点列表
        """
        changes = []
        window_ms = int(window_size * 1000)
        prev_volume = None
        
        for i in range(0, len(audio), window_ms):
            window = audio[i:i + window_ms]
            if len(window) < window_ms // 2:
                break
            
            volume = window.dBFS
            time_seconds = i / 1000.0
            
            if prev_volume is not None:
                # 计算音量变化率
                if prev_volume != -float('inf') and volume != -float('inf'):
                    change_ratio = abs(volume - prev_volume) / max(abs(prev_volume), 1)
                    
                    if change_ratio > threshold:
                        changes.append({
                            'time': time_seconds,
                            'prev_volume': prev_volume,
                            'curr_volume': volume,
                            'change_ratio': change_ratio
                        })
            
            prev_volume = volume
        
        self.logger.info(f"检测到 {len(changes)} 个音量变化点")
        return changes
    
    def detect_silence(self, audio: AudioSegment, 
                      min_silence_len: int = 1000,
                      silence_thresh: int = -40) -> List[Tuple[int, int]]:
        """
        检测静音段
        
        Args:
            audio: 音频对象
            min_silence_len: 最小静音长度（毫秒）
            silence_thresh: 静音阈值（dBFS）
            
        Returns:
            静音段时间列表 [(start_ms, end_ms), ...]
        """
        silence_ranges = detect_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )
        
        self.logger.info(f"检测到 {len(silence_ranges)} 个静音段")
        return silence_ranges
    
    def analyze_audio_energy(self, audio: AudioSegment, 
                            segment_duration: float = 0.5) -> List[Dict]:
        """
        分析音频能量分布
        
        Args:
            audio: 音频对象
            segment_duration: 分段时长（秒）
            
        Returns:
            能量分析结果列表
        """
        segment_ms = int(segment_duration * 1000)
        energy_data = []
        
        for i in range(0, len(audio), segment_ms):
            segment = audio[i:i + segment_ms]
            if len(segment) < segment_ms // 2:
                break
            
            # 计算能量（RMS）
            samples = np.array(segment.get_array_of_samples())
            rms = np.sqrt(np.mean(samples**2))
            
            # 归一化到0-1范围
            max_amplitude = 2**(segment.sample_width * 8 - 1)
            normalized_energy = min(rms / max_amplitude, 1.0)
            
            energy_data.append({
                'time': i / 1000.0,
                'energy': normalized_energy,
                'db': segment.dBFS
            })
        
        return energy_data
    
    def calculate_audio_score(self, audio_path: str, 
                            start_time: float, 
                            end_time: float) -> float:
        """
        计算音频片段的兴趣度分数
        
        Args:
            audio_path: 音频文件路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            兴趣度分数（0-1）
        """
        try:
            audio = self.load_audio(audio_path)
            
            # 提取片段
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            segment = audio[start_ms:end_ms]
            
            # 计算能量变化
            energy_data = self.analyze_audio_energy(segment, segment_duration=0.5)
            if not energy_data:
                return 0.0
            
            energies = [d['energy'] for d in energy_data]
            
            # 计算统计特征
            avg_energy = np.mean(energies)
            energy_variance = np.var(energies)
            max_energy = np.max(energies)
            
            # 检测音量变化
            volume_changes = self.detect_volume_changes(segment, window_size=1.0, threshold=0.2)
            change_score = min(len(volume_changes) / 10.0, 1.0)
            
            # 综合评分
            score = (
                avg_energy * 0.3 +
                energy_variance * 2.0 * 0.3 +  # 能量方差越大越有趣
                change_score * 0.4
            )
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"计算音频分数失败: {e}")
            return 0.0
    
    def get_audio_features(self, audio_path: str) -> Dict:
        """
        获取音频的综合特征
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            特征字典
        """
        audio = self.load_audio(audio_path)
        
        # 能量分析
        energy_data = self.analyze_audio_energy(audio)
        energies = [d['energy'] for d in energy_data]
        
        # 音量变化
        volume_changes = self.detect_volume_changes(audio)
        
        # 静音检测
        silence_ranges = self.detect_silence(audio)
        silence_duration = sum(end - start for start, end in silence_ranges) / 1000.0
        
        features = {
            'duration': len(audio) / 1000.0,
            'avg_energy': np.mean(energies) if energies else 0,
            'max_energy': np.max(energies) if energies else 0,
            'energy_variance': np.var(energies) if energies else 0,
            'volume_changes': len(volume_changes),
            'silence_count': len(silence_ranges),
            'silence_duration': silence_duration,
            'silence_ratio': silence_duration / (len(audio) / 1000.0) if len(audio) > 0 else 0
        }
        
        self.logger.debug(f"音频特征: {features}")
        return features

"""
音频分析模块
分析音频特征，检测音量变化、静音段等
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
from typing import List, Dict, Tuple
from utils.logger import LoggerMixin


class AudioAnalyzer(LoggerMixin):
    """音频分析器"""
    
    def __init__(self):
        """初始化音频分析器"""
        super().__init__()
    
    def load_audio(self, audio_path: str) -> Tuple[int, np.ndarray]:
        """
        加载音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            (sample_rate, audio_data)
        """
        try:
            sample_rate, audio_data = wavfile.read(audio_path)
            
            # 如果是立体声，转换为单声道
            if len(audio_data.shape) == 2:
                audio_data = np.mean(audio_data, axis=1)
            
            # 归一化到[-1, 1]
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            
            self.logger.debug(f"音频加载成功: {audio_path}, 采样率: {sample_rate}Hz")
            return sample_rate, audio_data
        except Exception as e:
            self.logger.error(f"音频加载失败: {e}")
            raise
    
    def detect_volume_changes(self, audio_path: str, 
                            window_size: float = 1.0,
                            threshold: float = 0.3) -> List[Dict]:
        """
        检测音量变化点
        
        Args:
            audio_path: 音频文件路径
            window_size: 窗口大小（秒）
            threshold: 变化阈值（0-1）
            
        Returns:
            音量变化点列表
        """
        sample_rate, audio_data = self.load_audio(audio_path)
        
        changes = []
        window_samples = int(window_size * sample_rate)
        prev_rms = None
        
        for i in range(0, len(audio_data), window_samples):
            window = audio_data[i:i + window_samples]
            if len(window) < window_samples // 2:
                break
            
            # 计算RMS（均方根）音量
            rms = np.sqrt(np.mean(window**2))
            time_seconds = i / sample_rate
            
            if prev_rms is not None and prev_rms > 1e-6:
                change_ratio = abs(rms - prev_rms) / max(prev_rms, 1e-6)
                
                if change_ratio > threshold:
                    changes.append({
                        'time': time_seconds,
                        'prev_volume': float(prev_rms),
                        'curr_volume': float(rms),
                        'change_ratio': float(change_ratio)
                    })
            
            prev_rms = rms
        
        self.logger.info(f"检测到 {len(changes)} 个音量变化点")
        return changes
    
    def detect_silence(self, audio_path: str, 
                      min_silence_len: float = 1.0,
                      silence_thresh: float = 0.01) -> List[Tuple[float, float]]:
        """
        检测静音段
        
        Args:
            audio_path: 音频文件路径
            min_silence_len: 最小静音长度（秒）
            silence_thresh: 静音阈值（0-1，RMS值）
            
        Returns:
            静音段时间列表 [(start_sec, end_sec), ...]
        """
        sample_rate, audio_data = self.load_audio(audio_path)
        
        # 计算每个窗口的能量
        window_samples = int(0.1 * sample_rate)  # 100ms窗口
        is_silent = []
        
        for i in range(0, len(audio_data), window_samples):
            window = audio_data[i:i + window_samples]
            rms = np.sqrt(np.mean(window**2))
            is_silent.append(rms < silence_thresh)
        
        # 查找连续的静音段
        silence_ranges = []
        start = None
        min_windows = int(min_silence_len / 0.1)
        
        for i, silent in enumerate(is_silent):
            if silent and start is None:
                start = i
            elif not silent and start is not None:
                if i - start >= min_windows:
                    start_sec = start * 0.1
                    end_sec = i * 0.1
                    silence_ranges.append((start_sec, end_sec))
                start = None
        
        # 处理最后一个静音段
        if start is not None and len(is_silent) - start >= min_windows:
            start_sec = start * 0.1
            end_sec = len(is_silent) * 0.1
            silence_ranges.append((start_sec, end_sec))
        
        self.logger.info(f"检测到 {len(silence_ranges)} 个静音段")
        return silence_ranges
    
    def analyze_audio_energy(self, audio_path: str, 
                            segment_duration: float = 0.5) -> List[Dict]:
        """
        分析音频能量分布
        
        Args:
            audio_path: 音频文件路径
            segment_duration: 分段时长（秒）
            
        Returns:
            能量分析结果列表
        """
        sample_rate, audio_data = self.load_audio(audio_path)
        
        segment_samples = int(segment_duration * sample_rate)
        energy_data = []
        
        for i in range(0, len(audio_data), segment_samples):
            segment = audio_data[i:i + segment_samples]
            if len(segment) < segment_samples // 2:
                break
            
            # 计算RMS能量
            rms = np.sqrt(np.mean(segment**2))
            
            # 计算dB值
            db = 20 * np.log10(rms + 1e-10)  # 避免log(0)
            
            energy_data.append({
                'time': i / sample_rate,
                'energy': float(rms),
                'db': float(db)
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
            sample_rate, audio_data = self.load_audio(audio_path)
            
            # 提取片段
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            segment = audio_data[start_sample:end_sample]
            
            if len(segment) == 0:
                return 0.0
            
            # 计算能量数据
            window_samples = int(0.5 * sample_rate)
            energies = []
            
            for i in range(0, len(segment), window_samples):
                window = segment[i:i + window_samples]
                if len(window) > 0:
                    rms = np.sqrt(np.mean(window**2))
                    energies.append(rms)
            
            if not energies:
                return 0.0
            
            energies = np.array(energies)
            
            # 计算统计特征
            avg_energy = np.mean(energies)
            energy_variance = np.var(energies)
            max_energy = np.max(energies)
            
            # 计算音量变化次数
            changes = 0
            for i in range(1, len(energies)):
                if abs(energies[i] - energies[i-1]) > 0.1:
                    changes += 1
            change_score = min(changes / 10.0, 1.0)
            
            # 综合评分
            score = (
                avg_energy * 0.3 +
                energy_variance * 2.0 * 0.3 +
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
        sample_rate, audio_data = self.load_audio(audio_path)
        duration = len(audio_data) / sample_rate
        
        # 能量分析
        energy_data = self.analyze_audio_energy(audio_path)
        energies = [d['energy'] for d in energy_data]
        
        # 音量变化
        volume_changes = self.detect_volume_changes(audio_path)
        
        # 静音检测
        silence_ranges = self.detect_silence(audio_path)
        silence_duration = sum(end - start for start, end in silence_ranges)
        
        features = {
            'duration': duration,
            'avg_energy': float(np.mean(energies)) if energies else 0,
            'max_energy': float(np.max(energies)) if energies else 0,
            'energy_variance': float(np.var(energies)) if energies else 0,
            'volume_changes': len(volume_changes),
            'silence_count': len(silence_ranges),
            'silence_duration': silence_duration,
            'silence_ratio': silence_duration / duration if duration > 0 else 0
        }
        
        self.logger.debug(f"音频特征: {features}")
        return features


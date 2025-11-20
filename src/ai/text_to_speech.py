"""
文本转语音模块
提供基于pyttsx3的本地TTS功能
"""

import pyttsx3
import os
from pathlib import Path
from typing import Optional, List
from utils.logger import setup_logger


class TextToSpeech:
    """文本转语音类"""
    
    def __init__(self, config: dict):
        """
        初始化TTS引擎
        
        Args:
            config: 配置字典，包含rate, volume, voice等参数
        """
        self.logger = setup_logger()
        self.config = config
        self.engine = None
        
        try:
            self.engine = pyttsx3.init()
            self._configure()
            self.logger.info("TTS引擎初始化成功")
        except Exception as e:
            self.logger.error(f"TTS引擎初始化失败: {e}")
            raise
    
    def _configure(self):
        """配置TTS引擎参数"""
        if not self.engine:
            return
        
        # 设置语速 (words per minute)
        rate = self.config.get('rate', 150)
        self.engine.setProperty('rate', rate)
        
        # 设置音量 (0.0 - 1.0)
        volume = self.config.get('volume', 0.9)
        self.engine.setProperty('volume', volume)
        
        # 设置音色 (male/female)
        voice_gender = self.config.get('voice', 'female')
        self._set_voice(voice_gender)
        
        self.logger.info(f"TTS配置: 语速={rate}, 音量={volume}, 音色={voice_gender}")
    
    def _set_voice(self, gender: str = 'female'):
        """
        设置音色
        
        Args:
            gender: 音色性别，'male' 或 'female'
        """
        if not self.engine:
            return
        
        voices = self.engine.getProperty('voices')
        
        # Windows下使用SAPI5，通常第0个是男声，第1个是女声
        # 但这取决于系统安装的语音包
        if gender == 'male':
            voice_index = 0
        else:
            voice_index = 1 if len(voices) > 1 else 0
        
        if voices and voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            self.logger.debug(f"设置音色: {voices[voice_index].name}")
    
    def synthesize(self, text: str, output_path: str) -> bool:
        """
        将文本转换为语音文件
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        if not self.engine:
            self.logger.error("TTS引擎未初始化")
            return False
        
        if not text:
            self.logger.warning("输入文本为空")
            return False
        
        try:
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成语音
            self.logger.info(f"开始生成语音: {len(text)} 字符 -> {output_path}")
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            # 验证文件是否生成
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.logger.info(f"语音生成成功: {output_path}")
                return True
            else:
                self.logger.error("语音文件生成失败或为空")
                return False
                
        except Exception as e:
            self.logger.error(f"语音合成失败: {e}")
            return False
    
    def synthesize_from_subtitles(self, subtitle_segments: List[dict], output_path: str) -> bool:
        """
        从字幕片段生成完整配音
        
        Args:
            subtitle_segments: 字幕片段列表，每个片段包含 {'start': float, 'end': float, 'text': str}
            output_path: 输出音频文件路径
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        if not subtitle_segments:
            self.logger.warning("字幕片段为空")
            return False
        
        # 将所有字幕文本拼接成一段连续的文本
        # 注意：这种方式不考虑时间轴，适合简单的整体配音
        full_text = " ".join([segment['text'] for segment in subtitle_segments if segment.get('text')])
        
        return self.synthesize(full_text, output_path)
    
    def synthesize_timed_audio(self, subtitle_segments: List[dict], output_dir: str) -> List[dict]:
        """
        为每个字幕片段生成独立的音频文件（支持时间轴对齐）
        
        Args:
            subtitle_segments: 字幕片段列表
            output_dir: 输出目录
        
        Returns:
            List[dict]: 包含音频路径和时间信息的列表
        """
        audio_segments = []
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        for i, segment in enumerate(subtitle_segments):
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            # 生成独立的音频文件
            audio_filename = f"tts_segment_{i:04d}.wav"
            audio_path = output_dir_path / audio_filename
            
            if self.synthesize(text, str(audio_path)):
                audio_segments.append({
                    'audio_path': str(audio_path),
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': text
                })
                self.logger.debug(f"片段 {i} 配音完成: {text[:20]}...")
        
        self.logger.info(f"完成 {len(audio_segments)}/{len(subtitle_segments)} 个片段的配音")
        return audio_segments
    
    def get_available_voices(self) -> List[dict]:
        """
        获取系统可用的语音列表
        
        Returns:
            List[dict]: 语音信息列表，包含id, name, languages等
        """
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for voice in voices:
            voice_list.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages if hasattr(voice, 'languages') else [],
                'gender': voice.gender if hasattr(voice, 'gender') else 'unknown'
            })
        
        return voice_list
    
    def cleanup(self):
        """清理TTS引擎资源"""
        if self.engine:
            try:
                self.engine.stop()
                self.logger.debug("TTS引擎已停止")
            except:
                pass

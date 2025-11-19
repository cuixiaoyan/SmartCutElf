"""
语音合成模块 (TTS - Text-to-Speech)
支持本地pyttsx3引擎
"""

import pyttsx3
from pathlib import Path
from typing import Optional, List
from utils.logger import LoggerMixin


class TextToSpeech(LoggerMixin):
    """文本转语音"""
    
    def __init__(self):
        """初始化TTS引擎"""
        super().__init__()
        try:
            self.engine = pyttsx3.init()
            self._configure_engine()
            self.logger.info("TTS引擎初始化成功")
        except Exception as e:
            self.logger.error(f"TTS引擎初始化失败: {e}")
            self.engine = None
    
    def _configure_engine(self):
        """配置TTS引擎"""
        if not self.engine:
            return
        
        # 设置语速 (words per minute)
        self.engine.setProperty('rate', 150)
        
        # 设置音量 (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
    
    def get_available_voices(self) -> List[Dict]:
        """
        获取可用的语音列表
        
        Returns:
            语音信息列表
        """
        if not self.engine:
            return []
        
        voices_info = []
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            voices_info.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': voice.gender
            })
        
        return voices_info
    
    def set_voice(self, voice_id: Optional[str] = None, gender: str = "female"):
        """
        设置语音
        
        Args:
            voice_id: 语音ID，如果为None则根据gender选择
            gender: 性别 ("male" 或 "female")
        """
        if not self.engine:
            return
        
        voices = self.engine.getProperty('voices')
        
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # 根据性别选择
            for voice in voices:
                if gender.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    self.logger.info(f"已设置语音: {voice.name}")
                    break
    
    def set_rate(self, rate: int):
        """
        设置语速
        
        Args:
            rate: 语速 (words per minute, 默认200)
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """
        设置音量
        
        Args:
            volume: 音量 (0.0 - 1.0)
        """
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def synthesize(self, text: str, output_path: str) -> bool:
        """
        合成语音并保存到文件
        
        Args:
            text: 要合成的文本
            output_path: 输出音频文件路径
            
        Returns:
            是否成功
        """
        if not self.engine:
            self.logger.error("TTS引擎未初始化")
            return False
        
        try:
            self.logger.info(f"开始合成语音: {len(text)} 字符")
            
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            self.logger.info(f"语音文件生成成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"语音合成失败: {e}")
            return False
    
    def speak(self, text: str):
        """
        直接朗读文本（不保存文件）
        
        Args:
            text: 要朗读的文本
        """
        if not self.engine:
            self.logger.error("TTS引擎未初始化")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"朗读失败: {e}")
    
    def synthesize_segments(self, segments: List[str], output_dir: str) -> List[str]:
        """
        批量合成多个文本片段
        
        Args:
            segments: 文本片段列表
            output_dir: 输出目录
            
        Returns:
            生成的音频文件路径列表
        """
        output_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, text in enumerate(segments):
            audio_file = output_path / f"segment_{i:04d}.mp3"
            if self.synthesize(text, str(audio_file)):
                output_paths.append(str(audio_file))
        
        self.logger.info(f"批量合成完成，共 {len(output_paths)} 个文件")
        return output_paths

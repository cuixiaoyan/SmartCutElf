"""
语音识别模块
使用OpenAI Whisper进行语音转文字
"""

import whisper
from typing import List, Dict, Optional
from pathlib import Path
from utils.logger import LoggerMixin


class SpeechRecognizer(LoggerMixin):
    """语音识别器"""
    
    def __init__(self, model_size: str = "base"):
        """
        初始化语音识别器
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large)
        """
        super().__init__()
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载Whisper模型"""
        try:
            self.logger.info(f"正在加载Whisper模型: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.logger.info("模型加载成功")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise
    
    def transcribe(self, audio_path: str, language: str = "zh") -> Optional[Dict]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（zh=中文，en=英文）
            
        Returns:
            转录结果字典
        """
        if not self.model:
            self.logger.error("模型未加载")
            return None
        
        try:
            self.logger.info(f"开始转录音频: {audio_path}")
            
            # 执行转录
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            self.logger.info(f"转录完成，识别到 {len(result.get('segments', []))} 个片段")
            return result
            
        except Exception as e:
            self.logger.error(f"转录失败: {e}")
            return None
    
    def get_segments(self, audio_path: str, language: str = "zh") -> List[Dict]:
        """
        获取带时间戳的文本片段
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            
        Returns:
            片段列表，每个片段包含start, end, text
        """
        result = self.transcribe(audio_path, language)
        
        if not result or 'segments' not in result:
            return []
        
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'confidence': segment.get('no_speech_prob', 0)
            })
        
        return segments
    
    def get_full_text(self, audio_path: str, language: str = "zh") -> str:
        """
        获取完整文本（不带时间戳）
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            
        Returns:
            完整文本
        """
        result = self.transcribe(audio_path, language)
        
        if not result or 'text' not in result:
            return ""
        
        return result['text'].strip()

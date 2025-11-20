"""
错误处理和用户友好提示
提供详细的错误信息和解决方案
"""

from typing import Dict, Optional, Tuple
from pathlib import Path


class ErrorCode:
    """错误代码定义"""
    # 文件相关
    FILE_NOT_FOUND = "E001"
    FILE_INVALID = "E002"
    FILE_CORRUPTED = "E003"
    FILE_TOO_LARGE = "E004"
    
    # FFmpeg 相关
    FFMPEG_NOT_FOUND = "E101"
    FFMPEG_ERROR = "E102"
    CODEC_ERROR = "E103"
    
    # 处理相关
    PROCESSING_FAILED = "E201"
    MEMORY_ERROR = "E202"
    TIMEOUT_ERROR = "E203"
    
    # AI 相关
    WHISPER_ERROR = "E301"
    TTS_ERROR = "E302"
    
    # 配置相关
    CONFIG_ERROR = "E401"
    PATH_ERROR = "E402"


class ErrorSolution:
    """错误解决方案"""
    
    SOLUTIONS = {
        ErrorCode.FILE_NOT_FOUND: {
            "title": "文件未找到",
            "message": "指定的视频文件不存在或已被移动",
            "solutions": [
                "检查文件路径是否正确",
                "确认文件未被删除或移动",
                "尝试重新选择文件"
            ],
            "doc_link": None
        },
        
        ErrorCode.FILE_INVALID: {
            "title": "文件格式无效",
            "message": "文件格式不支持或文件已损坏",
            "solutions": [
                "确认文件是有效的视频文件",
                "支持的格式：MP4, AVI, MOV, MKV, WMV, FLV",
                "尝试用播放器打开文件检查是否损坏"
            ],
            "doc_link": "docs/使用说明.md#支持格式"
        },
        
        ErrorCode.FILE_CORRUPTED: {
            "title": "文件已损坏",
            "message": "视频文件可能已损坏，无法正常读取",
            "solutions": [
                "尝试用视频播放器打开文件",
                "使用视频修复工具修复文件",
                "重新下载或获取源文件"
            ],
            "doc_link": None
        },
        
        ErrorCode.FILE_TOO_LARGE: {
            "title": "文件过大",
            "message": "文件大小超过推荐处理范围",
            "solutions": [
                "建议处理小于 2GB 的文件",
                "可以先用其他工具分割视频",
                "增加系统内存或关闭其他程序"
            ],
            "doc_link": None
        },
        
        ErrorCode.FFMPEG_NOT_FOUND: {
            "title": "FFmpeg 未安装",
            "message": "未检测到 FFmpeg，这是视频处理的必需工具",
            "solutions": [
                "请按照安装指南安装 FFmpeg",
                "确认 FFmpeg 已添加到系统 PATH",
                "重启应用程序后重试"
            ],
            "doc_link": "docs/FFmpeg安装指南.md"
        },
        
        ErrorCode.FFMPEG_ERROR: {
            "title": "FFmpeg 处理错误",
            "message": "视频处理过程中出现错误",
            "solutions": [
                "检查视频文件是否完整",
                "确认磁盘空间充足",
                "查看详细日志了解具体错误"
            ],
            "doc_link": None
        },
        
        ErrorCode.CODEC_ERROR: {
            "title": "编解码器错误",
            "message": "视频编解码器不支持或缺失",
            "solutions": [
                "尝试使用 MP4 格式（H.264 编码）",
                "更新 FFmpeg 到最新版本",
                "转换视频格式后重试"
            ],
            "doc_link": "docs/使用说明.md#支持格式"
        },
        
        ErrorCode.PROCESSING_FAILED: {
            "title": "处理失败",
            "message": "视频处理过程中发生错误",
            "solutions": [
                "查看日志了解详细错误信息",
                "尝试减少并行处理数量",
                "检查输出目录是否有写入权限"
            ],
            "doc_link": None
        },
        
        ErrorCode.MEMORY_ERROR: {
            "title": "内存不足",
            "message": "系统内存不足，无法继续处理",
            "solutions": [
                "关闭其他占用内存的应用程序",
                "减少并行处理数量（设置中调整）",
                "处理较小的视频文件",
                "增加系统虚拟内存"
            ],
            "doc_link": "docs/使用说明.md#性能优化"
        },
        
        ErrorCode.TIMEOUT_ERROR: {
            "title": "处理超时",
            "message": "视频处理时间过长，已超时",
            "solutions": [
                "处理较短的视频文件",
                "使用更快的 Whisper 模型（tiny）",
                "增加超时时间限制"
            ],
            "doc_link": None
        },
        
        ErrorCode.WHISPER_ERROR: {
            "title": "语音识别错误",
            "message": "Whisper 模型加载或处理失败",
            "solutions": [
                "确认已安装 openai-whisper",
                "首次使用会自动下载模型，请耐心等待",
                "尝试使用更小的模型（tiny/base）",
                "或在设置中关闭字幕功能"
            ],
            "doc_link": "docs/启动指南.md#whisper-模型下载慢"
        },
        
        ErrorCode.TTS_ERROR: {
            "title": "语音合成错误",
            "message": "文本转语音功能出现错误",
            "solutions": [
                "确认已安装 pyttsx3",
                "检查系统音频设备是否正常",
                "或在设置中关闭配音功能"
            ],
            "doc_link": None
        },
        
        ErrorCode.CONFIG_ERROR: {
            "title": "配置错误",
            "message": "配置文件读取或解析失败",
            "solutions": [
                "检查 config.yaml 文件格式",
                "删除配置文件使用默认配置",
                "重新安装应用程序"
            ],
            "doc_link": None
        },
        
        ErrorCode.PATH_ERROR: {
            "title": "路径错误",
            "message": "文件路径包含非法字符或过长",
            "solutions": [
                "避免使用特殊字符",
                "缩短文件路径长度",
                "移动文件到更简单的路径"
            ],
            "doc_link": None
        }
    }
    
    @classmethod
    def get_solution(cls, error_code: str) -> Optional[Dict]:
        """获取错误解决方案"""
        return cls.SOLUTIONS.get(error_code)
    
    @classmethod
    def format_error_message(cls, error_code: str, detail: str = "") -> str:
        """格式化错误消息"""
        solution = cls.get_solution(error_code)
        if not solution:
            return f"错误代码: {error_code}\n{detail}"
        
        message = f"❌ {solution['title']}\n\n"
        message += f"📝 {solution['message']}\n"
        
        if detail:
            message += f"\n详细信息: {detail}\n"
        
        message += "\n💡 解决方案:\n"
        for i, sol in enumerate(solution['solutions'], 1):
            message += f"  {i}. {sol}\n"
        
        if solution['doc_link']:
            message += f"\n📖 查看文档: {solution['doc_link']}"
        
        return message


class UserFriendlyError(Exception):
    """用户友好的错误类"""
    
    def __init__(self, error_code: str, detail: str = "", original_error: Exception = None):
        self.error_code = error_code
        self.detail = detail
        self.original_error = original_error
        self.message = ErrorSolution.format_error_message(error_code, detail)
        super().__init__(self.message)
    
    def get_short_message(self) -> str:
        """获取简短错误消息"""
        solution = ErrorSolution.get_solution(self.error_code)
        if solution:
            return f"{solution['title']}: {solution['message']}"
        return self.detail or "未知错误"
    
    def get_solutions(self) -> list:
        """获取解决方案列表"""
        solution = ErrorSolution.get_solution(self.error_code)
        return solution['solutions'] if solution else []


def handle_exception(func):
    """异常处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserFriendlyError:
            raise
        except FileNotFoundError as e:
            raise UserFriendlyError(
                ErrorCode.FILE_NOT_FOUND,
                str(e),
                e
            )
        except MemoryError as e:
            raise UserFriendlyError(
                ErrorCode.MEMORY_ERROR,
                str(e),
                e
            )
        except Exception as e:
            # 尝试识别常见错误
            error_str = str(e).lower()
            
            if 'ffmpeg' in error_str or 'ffprobe' in error_str:
                raise UserFriendlyError(
                    ErrorCode.FFMPEG_NOT_FOUND,
                    str(e),
                    e
                )
            elif 'codec' in error_str:
                raise UserFriendlyError(
                    ErrorCode.CODEC_ERROR,
                    str(e),
                    e
                )
            elif 'whisper' in error_str:
                raise UserFriendlyError(
                    ErrorCode.WHISPER_ERROR,
                    str(e),
                    e
                )
            else:
                # 未知错误，保留原始异常
                raise
    
    return wrapper


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    验证文件路径
    
    Returns:
        (is_valid, error_code)
    """
    path = Path(file_path)
    
    # 检查文件是否存在
    if not path.exists():
        return False, ErrorCode.FILE_NOT_FOUND
    
    # 检查是否是文件
    if not path.is_file():
        return False, ErrorCode.FILE_INVALID
    
    # 检查文件大小（建议小于 2GB）
    file_size = path.stat().st_size
    if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
        return False, ErrorCode.FILE_TOO_LARGE
    
    # 检查文件扩展名
    valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm'}
    if path.suffix.lower() not in valid_extensions:
        return False, ErrorCode.FILE_INVALID
    
    return True, None

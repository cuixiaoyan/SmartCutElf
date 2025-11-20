"""
视频转场效果模块
支持多种转场效果：淡入淡出、交叉溶解、滑动切换、缩放转场等
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from enum import Enum


class TransitionType(Enum):
    """转场类型枚举"""
    NONE = "none"                    # 无转场
    FADE = "fade"                    # 淡入淡出
    DISSOLVE = "dissolve"            # 交叉溶解
    SLIDE_LEFT = "slide_left"        # 向左滑动
    SLIDE_RIGHT = "slide_right"      # 向右滑动
    SLIDE_UP = "slide_up"            # 向上滑动
    SLIDE_DOWN = "slide_down"        # 向下滑动
    ZOOM_IN = "zoom_in"              # 放大
    ZOOM_OUT = "zoom_out"            # 缩小
    WIPE_LEFT = "wipe_left"          # 左擦除
    WIPE_RIGHT = "wipe_right"        # 右擦除


class TransitionEffect:
    """转场效果基类"""
    
    def __init__(self, duration: float = 0.5):
        """
        初始化转场效果
        :param duration: 转场持续时间（秒）
        """
        self.duration = duration
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """
        应用转场效果
        :param frame1: 第一帧
        :param frame2: 第二帧
        :param progress: 进度 (0.0 到 1.0)
        :return: 混合后的帧
        """
        raise NotImplementedError("子类必须实现此方法")


class FadeTransition(TransitionEffect):
    """淡入淡出转场"""
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """淡入淡出效果"""
        alpha = progress
        beta = 1.0 - progress
        return cv2.addWeighted(frame1, beta, frame2, alpha, 0)


class DissolveTransition(TransitionEffect):
    """交叉溶解转场（与淡入淡出类似，但更平滑）"""
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """交叉溶解效果"""
        # 使用平滑的插值曲线
        smooth_progress = self._smooth_step(progress)
        alpha = smooth_progress
        beta = 1.0 - smooth_progress
        return cv2.addWeighted(frame1, beta, frame2, alpha, 0)
    
    @staticmethod
    def _smooth_step(x: float) -> float:
        """平滑步进函数"""
        return x * x * (3 - 2 * x)


class SlideTransition(TransitionEffect):
    """滑动转场"""
    
    def __init__(self, duration: float = 0.5, direction: str = "left"):
        """
        初始化滑动转场
        :param duration: 转场持续时间
        :param direction: 滑动方向 (left, right, up, down)
        """
        super().__init__(duration)
        self.direction = direction
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """滑动效果"""
        height, width = frame1.shape[:2]
        result = np.zeros_like(frame1)
        
        if self.direction == "left":
            offset = int(width * progress)
            result[:, :width-offset] = frame1[:, offset:]
            result[:, width-offset:] = frame2[:, :offset]
        elif self.direction == "right":
            offset = int(width * progress)
            result[:, offset:] = frame1[:, :width-offset]
            result[:, :offset] = frame2[:, width-offset:]
        elif self.direction == "up":
            offset = int(height * progress)
            result[:height-offset, :] = frame1[offset:, :]
            result[height-offset:, :] = frame2[:offset, :]
        elif self.direction == "down":
            offset = int(height * progress)
            result[offset:, :] = frame1[:height-offset, :]
            result[:offset, :] = frame2[height-offset:, :]
        
        return result


class ZoomTransition(TransitionEffect):
    """缩放转场"""
    
    def __init__(self, duration: float = 0.5, zoom_type: str = "in"):
        """
        初始化缩放转场
        :param duration: 转场持续时间
        :param zoom_type: 缩放类型 (in: 放大, out: 缩小)
        """
        super().__init__(duration)
        self.zoom_type = zoom_type
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """缩放效果"""
        height, width = frame1.shape[:2]
        
        if self.zoom_type == "in":
            # 第一帧放大淡出，第二帧淡入
            scale = 1.0 + progress * 0.5
            alpha = 1.0 - progress
        else:
            # 第一帧缩小淡出，第二帧淡入
            scale = 1.0 - progress * 0.3
            alpha = 1.0 - progress
        
        # 缩放第一帧
        center_x, center_y = width // 2, height // 2
        M = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
        frame1_scaled = cv2.warpAffine(frame1, M, (width, height))
        
        # 混合两帧
        beta = progress
        return cv2.addWeighted(frame1_scaled, alpha, frame2, beta, 0)


class WipeTransition(TransitionEffect):
    """擦除转场"""
    
    def __init__(self, duration: float = 0.5, direction: str = "left"):
        """
        初始化擦除转场
        :param duration: 转场持续时间
        :param direction: 擦除方向 (left, right)
        """
        super().__init__(duration)
        self.direction = direction
    
    def apply(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """擦除效果"""
        height, width = frame1.shape[:2]
        result = frame1.copy()
        
        if self.direction == "left":
            split_pos = int(width * progress)
            result[:, :split_pos] = frame2[:, :split_pos]
        elif self.direction == "right":
            split_pos = int(width * (1 - progress))
            result[:, split_pos:] = frame2[:, split_pos:]
        
        return result


class TransitionManager:
    """转场管理器"""
    
    def __init__(self):
        """初始化转场管理器"""
        self.transitions = {
            TransitionType.FADE: FadeTransition,
            TransitionType.DISSOLVE: DissolveTransition,
            TransitionType.SLIDE_LEFT: lambda d: SlideTransition(d, "left"),
            TransitionType.SLIDE_RIGHT: lambda d: SlideTransition(d, "right"),
            TransitionType.SLIDE_UP: lambda d: SlideTransition(d, "up"),
            TransitionType.SLIDE_DOWN: lambda d: SlideTransition(d, "down"),
            TransitionType.ZOOM_IN: lambda d: ZoomTransition(d, "in"),
            TransitionType.ZOOM_OUT: lambda d: ZoomTransition(d, "out"),
            TransitionType.WIPE_LEFT: lambda d: WipeTransition(d, "left"),
            TransitionType.WIPE_RIGHT: lambda d: WipeTransition(d, "right"),
        }
    
    def create_transition(self, transition_type: TransitionType, duration: float = 0.5) -> Optional[TransitionEffect]:
        """
        创建转场效果
        :param transition_type: 转场类型
        :param duration: 转场持续时间
        :return: 转场效果对象
        """
        if transition_type == TransitionType.NONE:
            return None
        
        transition_class = self.transitions.get(transition_type)
        if transition_class:
            if callable(transition_class):
                return transition_class(duration)
            return transition_class(duration)
        
        return None
    
    def apply_transition_between_clips(self, 
                                       clip1_path: str, 
                                       clip2_path: str,
                                       output_path: str,
                                       transition_type: TransitionType = TransitionType.FADE,
                                       transition_duration: float = 0.5) -> bool:
        """
        在两个视频片段之间应用转场效果
        :param clip1_path: 第一个片段路径
        :param clip2_path: 第二个片段路径
        :param output_path: 输出路径
        :param transition_type: 转场类型
        :param transition_duration: 转场持续时间
        :return: 是否成功
        """
        try:
            # 打开视频
            cap1 = cv2.VideoCapture(clip1_path)
            cap2 = cv2.VideoCapture(clip2_path)
            
            if not cap1.isOpened() or not cap2.isOpened():
                return False
            
            # 获取视频属性
            fps = int(cap1.get(cv2.CAP_PROP_FPS))
            width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 创建输出视频
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 创建转场效果
            transition = self.create_transition(transition_type, transition_duration)
            
            # 写入第一个片段（除了最后几帧）
            transition_frames = int(fps * transition_duration)
            frame_count1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
            
            for i in range(frame_count1 - transition_frames):
                ret, frame = cap1.read()
                if not ret:
                    break
                out.write(frame)
            
            # 获取转场需要的帧
            clip1_transition_frames = []
            for i in range(transition_frames):
                ret, frame = cap1.read()
                if ret:
                    clip1_transition_frames.append(frame)
            
            clip2_transition_frames = []
            for i in range(transition_frames):
                ret, frame = cap2.read()
                if ret:
                    clip2_transition_frames.append(frame)
            
            # 应用转场效果
            if transition and clip1_transition_frames and clip2_transition_frames:
                for i in range(min(len(clip1_transition_frames), len(clip2_transition_frames))):
                    progress = i / len(clip1_transition_frames)
                    blended_frame = transition.apply(
                        clip1_transition_frames[i],
                        clip2_transition_frames[i],
                        progress
                    )
                    out.write(blended_frame)
            
            # 写入第二个片段的剩余部分
            while True:
                ret, frame = cap2.read()
                if not ret:
                    break
                out.write(frame)
            
            # 释放资源
            cap1.release()
            cap2.release()
            out.release()
            
            return True
            
        except Exception as e:
            print(f"转场效果应用失败: {e}")
            return False
    
    @staticmethod
    def get_available_transitions() -> list:
        """获取可用的转场类型列表"""
        return [t for t in TransitionType]

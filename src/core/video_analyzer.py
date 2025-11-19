"""
视频分析模块
分析视频的视觉特征，包括场景检测、运动检测等
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from utils.logger import LoggerMixin


class VideoAnalyzer(LoggerMixin):
    """视频分析器"""
    
    def __init__(self):
        """初始化视频分析器"""
        super().__init__()
    
    def detect_scene_changes(self, video_path: str, threshold: float = 0.3) -> List[float]:
        """
        检测场景变化点
        
        Args:
            video_path: 视频文件路径
            threshold: 场景变化阈值（0-1）
            
        Returns:
            场景变化时间点列表（秒）
        """
        scene_changes = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"无法打开视频: {video_path}")
            return scene_changes
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        prev_hist = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每5帧检测一次（提高性能）
            if frame_count % 5 == 0:
                # 计算颜色直方图
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], 
                                   [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # 计算直方图相关性
                    correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    # 相关性低表示场景变化
                    if correlation < (1 - threshold):
                        time_seconds = frame_count / fps
                        scene_changes.append(time_seconds)
                        self.logger.debug(f"场景变化: {time_seconds:.2f}秒")
                
                prev_hist = hist
            
            frame_count += 1
        
        cap.release()
        self.logger.info(f"检测到 {len(scene_changes)} 个场景变化")
        return scene_changes
    
    def detect_motion_intensity(self, video_path: str, 
                               sample_interval: int = 5) -> List[Dict]:
        """
        检测视频运动强度
        
        Args:
            video_path: 视频文件路径
            sample_interval: 采样间隔（帧数）
            
        Returns:
            运动强度数据列表
        """
        motion_data = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"无法打开视频: {video_path}")
            return motion_data
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        prev_gray = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_gray is not None:
                    # 计算帧差
                    diff = cv2.absdiff(prev_gray, gray)
                    motion_score = np.mean(diff) / 255.0
                    
                    motion_data.append({
                        'frame': frame_count,
                        'time': frame_count / fps,
                        'intensity': motion_score
                    })
                
                prev_gray = gray
            
            frame_count += 1
        
        cap.release()
        self.logger.info(f"运动检测完成，{len(motion_data)} 个数据点")
        return motion_data
    
    def detect_faces(self, video_path: str, sample_interval: int = 30) -> List[Dict]:
        """
        检测视频中的人脸
        
        Args:
            video_path: 视频文件路径
            sample_interval: 采样间隔（帧数）
            
        Returns:
            人脸检测结果列表
        """
        face_data = []
        
        # 加载人脸检测器
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"无法打开视频: {video_path}")
            return face_data
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                face_data.append({
                    'frame': frame_count,
                    'time': frame_count / fps,
                    'face_count': len(faces),
                    'has_face': len(faces) > 0
                })
            
            frame_count += 1
        
        cap.release()
        self.logger.info(f"人脸检测完成，{len(face_data)} 个数据点")
        return face_data
    
    def calculate_video_score(self, video_path: str, 
                            start_time: float, 
                            end_time: float) -> float:
        """
        计算视频片段的兴趣度分数
        
        Args:
            video_path: 视频文件路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            兴趣度分数（0-1）
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return 0.0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            motion_scores = []
            prev_gray = None
            current_frame = start_frame
            
            while current_frame < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    motion_score = np.mean(diff) / 255.0
                    motion_scores.append(motion_score)
                
                prev_gray = gray
                current_frame += 1
            
            cap.release()
            
            if not motion_scores:
                return 0.0
            
            # 计算特征
            avg_motion = np.mean(motion_scores)
            motion_variance = np.var(motion_scores)
            max_motion = np.max(motion_scores)
            
            # 综合评分
            score = (
                avg_motion * 0.4 +
                motion_variance * 10.0 * 0.3 +  # 方差越大越有趣
                max_motion * 0.3
            )
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"计算视频分数失败: {e}")
            return 0.0
    
    def extract_frames(self, video_path: str, output_dir: str, 
                      interval: float = 1.0) -> List[str]:
        """
        从视频中提取关键帧
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            interval: 提取间隔（秒）
            
        Returns:
            提取的帧图片路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        frame_paths = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            self.logger.error(f"无法打开视频: {video_path}")
            return frame_paths
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval)
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_path = output_path / f"frame_{saved_count:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(str(frame_path))
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        self.logger.info(f"提取了 {len(frame_paths)} 帧")
        return frame_paths

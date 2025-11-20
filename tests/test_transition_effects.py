"""
转场效果测试
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.transition_effects import (
    TransitionType, TransitionManager,
    FadeTransition, DissolveTransition,
    SlideTransition, ZoomTransition, WipeTransition
)


class TestTransitionEffects(unittest.TestCase):
    """转场效果测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试帧（100x100 RGB图像）
        self.frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        self.frame1[:, :] = [255, 0, 0]  # 红色
        
        self.frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
        self.frame2[:, :] = [0, 0, 255]  # 蓝色
    
    def test_fade_transition(self):
        """测试淡入淡出转场"""
        transition = FadeTransition(duration=0.5)
        
        # 测试开始时（progress=0）应该接近frame1
        result_start = transition.apply(self.frame1, self.frame2, 0.0)
        np.testing.assert_array_almost_equal(result_start, self.frame1)
        
        # 测试结束时（progress=1）应该接近frame2
        result_end = transition.apply(self.frame1, self.frame2, 1.0)
        np.testing.assert_array_almost_equal(result_end, self.frame2)
        
        # 测试中间时应该是混合
        result_mid = transition.apply(self.frame1, self.frame2, 0.5)
        self.assertFalse(np.array_equal(result_mid, self.frame1))
        self.assertFalse(np.array_equal(result_mid, self.frame2))
    
    def test_dissolve_transition(self):
        """测试交叉溶解转场"""
        transition = DissolveTransition(duration=0.5)
        
        result_start = transition.apply(self.frame1, self.frame2, 0.0)
        result_end = transition.apply(self.frame1, self.frame2, 1.0)
        
        # 验证开始和结束状态
        np.testing.assert_array_almost_equal(result_start, self.frame1, decimal=0)
        np.testing.assert_array_almost_equal(result_end, self.frame2, decimal=0)
    
    def test_slide_transition_left(self):
        """测试向左滑动转场"""
        transition = SlideTransition(duration=0.5, direction="left")
        
        result = transition.apply(self.frame1, self.frame2, 0.5)
        
        # 验证结果形状正确
        self.assertEqual(result.shape, self.frame1.shape)
        
        # 验证左半部分应该是frame2，右半部分应该是frame1
        left_part = result[:, :50]
        right_part = result[:, 50:]
        
        # 左半部分应该主要是蓝色（frame2）
        self.assertTrue(np.mean(left_part[:, :, 2]) > np.mean(left_part[:, :, 0]))
    
    def test_slide_transition_right(self):
        """测试向右滑动转场"""
        transition = SlideTransition(duration=0.5, direction="right")
        
        result = transition.apply(self.frame1, self.frame2, 0.5)
        self.assertEqual(result.shape, self.frame1.shape)
    
    def test_zoom_transition_in(self):
        """测试放大转场"""
        transition = ZoomTransition(duration=0.5, zoom_type="in")
        
        result = transition.apply(self.frame1, self.frame2, 0.5)
        self.assertEqual(result.shape, self.frame1.shape)
    
    def test_zoom_transition_out(self):
        """测试缩小转场"""
        transition = ZoomTransition(duration=0.5, zoom_type="out")
        
        result = transition.apply(self.frame1, self.frame2, 0.5)
        self.assertEqual(result.shape, self.frame1.shape)
    
    def test_wipe_transition_left(self):
        """测试左擦除转场"""
        transition = WipeTransition(duration=0.5, direction="left")
        
        result = transition.apply(self.frame1, self.frame2, 0.5)
        
        # 验证结果形状
        self.assertEqual(result.shape, self.frame1.shape)
        
        # 验证左半部分是frame2，右半部分是frame1
        left_part = result[:, :50]
        right_part = result[:, 50:]
        
        np.testing.assert_array_equal(left_part, self.frame2[:, :50])
        np.testing.assert_array_equal(right_part, self.frame1[:, 50:])
    
    def test_transition_manager_create(self):
        """测试转场管理器创建转场"""
        manager = TransitionManager()
        
        # 测试创建淡入淡出转场
        fade = manager.create_transition(TransitionType.FADE, duration=1.0)
        self.assertIsInstance(fade, FadeTransition)
        self.assertEqual(fade.duration, 1.0)
        
        # 测试创建交叉溶解转场
        dissolve = manager.create_transition(TransitionType.DISSOLVE)
        self.assertIsInstance(dissolve, DissolveTransition)
        
        # 测试创建无转场
        none_transition = manager.create_transition(TransitionType.NONE)
        self.assertIsNone(none_transition)
    
    def test_transition_manager_available_transitions(self):
        """测试获取可用转场列表"""
        available = TransitionManager.get_available_transitions()
        
        self.assertIsInstance(available, list)
        self.assertGreater(len(available), 0)
        self.assertIn(TransitionType.FADE, available)
        self.assertIn(TransitionType.DISSOLVE, available)
    
    def test_transition_progress_range(self):
        """测试转场进度范围"""
        transition = FadeTransition()
        
        # 测试边界值
        result_0 = transition.apply(self.frame1, self.frame2, 0.0)
        result_1 = transition.apply(self.frame1, self.frame2, 1.0)
        
        self.assertEqual(result_0.shape, self.frame1.shape)
        self.assertEqual(result_1.shape, self.frame2.shape)
        
        # 测试中间值
        for progress in [0.25, 0.5, 0.75]:
            result = transition.apply(self.frame1, self.frame2, progress)
            self.assertEqual(result.shape, self.frame1.shape)


if __name__ == '__main__':
    unittest.main()

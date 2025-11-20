"""
配置管理测试
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.config import Config


class TestConfig(unittest.TestCase):
    """配置管理测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.test_config_file.write("""
app:
  name: TestApp
  version: 1.0.0

processing:
  max_workers: 4
  target_duration_min: 180
  target_duration_max: 300

ui:
  theme: dark
""")
        self.test_config_file.close()
        self.config = Config(self.test_config_file.name)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_config_file.name):
            os.unlink(self.test_config_file.name)
    
    def test_get_existing_key(self):
        """测试获取存在的配置项"""
        self.assertEqual(self.config.get('app.name'), 'TestApp')
        self.assertEqual(self.config.get('app.version'), '1.0.0')
        self.assertEqual(self.config.get('processing.max_workers'), 4)
    
    def test_get_nested_key(self):
        """测试获取嵌套配置项"""
        self.assertEqual(self.config.get('processing.target_duration_min'), 180)
        self.assertEqual(self.config.get('processing.target_duration_max'), 300)
    
    def test_get_nonexistent_key_with_default(self):
        """测试获取不存在的配置项（带默认值）"""
        result = self.config.get('nonexistent.key', 'default_value')
        self.assertEqual(result, 'default_value')
    
    def test_get_nonexistent_key_without_default(self):
        """测试获取不存在的配置项（不带默认值）"""
        result = self.config.get('nonexistent.key')
        self.assertIsNone(result)
    
    def test_set_existing_key(self):
        """测试设置已存在的配置项"""
        self.config.set('app.name', 'NewAppName')
        self.assertEqual(self.config.get('app.name'), 'NewAppName')
    
    def test_set_new_key(self):
        """测试设置新配置项"""
        self.config.set('new.key', 'new_value')
        self.assertEqual(self.config.get('new.key'), 'new_value')
    
    def test_set_nested_new_key(self):
        """测试设置嵌套的新配置项"""
        self.config.set('new.nested.key', 'nested_value')
        self.assertEqual(self.config.get('new.nested.key'), 'nested_value')
    
    def test_save_and_reload(self):
        """测试保存和重新加载配置"""
        # 修改配置
        self.config.set('app.name', 'ModifiedName')
        self.config.set('new.setting', 'test_value')
        
        # 保存配置
        self.config.save()
        
        # 重新加载配置
        new_config = Config(self.test_config_file.name)
        
        # 验证修改已保存
        self.assertEqual(new_config.get('app.name'), 'ModifiedName')
        self.assertEqual(new_config.get('new.setting'), 'test_value')
    
    def test_get_all_config(self):
        """测试获取所有配置"""
        all_config = self.config.get_all()
        
        self.assertIsInstance(all_config, dict)
        self.assertIn('app', all_config)
        self.assertIn('processing', all_config)
        self.assertIn('ui', all_config)


if __name__ == '__main__':
    unittest.main()

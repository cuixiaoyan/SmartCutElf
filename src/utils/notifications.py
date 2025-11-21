"""
系统通知和用户提示
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Windows上隐藏subprocess控制台窗口
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


class SystemNotifier:
    """系统通知器"""
    
    @staticmethod
    def is_windows() -> bool:
        """检查是否是 Windows 系统"""
        return os.name == 'nt'
    
    @staticmethod
    def notify(title: str, message: str, icon: str = "info"):
        """
        发送系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
            icon: 图标类型 (info, warning, error)
        """
        if SystemNotifier.is_windows():
            SystemNotifier._notify_windows(title, message, icon)
        else:
            SystemNotifier._notify_linux(title, message)
    
    @staticmethod
    def _notify_windows(title: str, message: str, icon: str = "info"):
        """Windows 系统通知"""
        try:
            # 使用 PowerShell 发送通知
            icon_map = {
                "info": "Info",
                "warning": "Warning",
                "error": "Error"
            }
            
            ps_icon = icon_map.get(icon, "Info")
            
            # 转义特殊字符
            title = title.replace('"', '""').replace("'", "''")
            message = message.replace('"', '""').replace("'", "''")
            
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message}</text>
                    </binding>
                </visual>
            </toast>
"@
            
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SmartCutElf").Show($toast)
            '''
            
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"发送通知失败: {e}")
    
    @staticmethod
    def _notify_linux(title: str, message: str):
        """Linux 系统通知"""
        try:
            subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
        except:
            pass


class FileOperations:
    """文件操作工具"""
    
    @staticmethod
    def open_folder(folder_path: str):
        """在文件管理器中打开文件夹"""
        path = Path(folder_path)
        
        if not path.exists():
            return False
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(path))
            elif os.name == 'posix':  # Linux/Mac
                if os.uname().sysname == 'Darwin':  # Mac
                    subprocess.run(['open', str(path)], creationflags=CREATE_NO_WINDOW)
                else:  # Linux
                    subprocess.run(['xdg-open', str(path)], creationflags=CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"打开文件夹失败: {e}")
            return False
    
    @staticmethod
    def open_file(file_path: str):
        """用默认程序打开文件"""
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(path))
            elif os.name == 'posix':  # Linux/Mac
                if os.uname().sysname == 'Darwin':  # Mac
                    subprocess.run(['open', str(path)], creationflags=CREATE_NO_WINDOW)
                else:  # Linux
                    subprocess.run(['xdg-open', str(path)], creationflags=CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"打开文件失败: {e}")
            return False
    
    @staticmethod
    def reveal_in_folder(file_path: str):
        """在文件管理器中显示文件"""
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', '/select,', str(path)], creationflags=CREATE_NO_WINDOW)
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':  # Mac
                    subprocess.run(['open', '-R', str(path)], creationflags=CREATE_NO_WINDOW)
                else:  # Linux
                    # 打开父文件夹
                    subprocess.run(['xdg-open', str(path.parent)], creationflags=CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"显示文件失败: {e}")
            return False


class QuickActions:
    """快捷操作"""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """复制文本到剪贴板"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            return True
        except Exception as e:
            print(f"复制到剪贴板失败: {e}")
            return False
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时长"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

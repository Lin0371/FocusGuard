"""FocusGuard 全局配置"""
import os

# ========== 路径处理 (适配 PyInstaller 打包) ==========
import sys

def get_app_dir():
    """获取程序所在的持久化路径（如果是 EXE，则是 EXE 所在文件夹；如果是脚本，则是脚本目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_dir():
    """获取资源文件路径（如果是 EXE，则指向临时解压目录 _MEIPASS；如果是脚本，则是脚本目录）"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
RES_DIR = get_resource_dir()

DATA_DIR = os.path.join(APP_DIR, "data")
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
LOG_FILE = os.path.join(DATA_DIR, "review_log.md")
ICON_PATH = os.path.join(RES_DIR, "assets", "icon.ico")

# ========== 定时器 ==========
MIN_INTERVAL = 30 * 60   # 最短间隔：30 分钟
MAX_INTERVAL = 90 * 60   # 最长间隔：90 分钟

# ========== 弹窗 ==========
MIN_INPUT_LENGTH = 3      # 最少输入字数才能提交

# ========== 调试模式 ==========
# 设为 True 时缩短间隔为 10~20 秒，方便测试
DEBUG = False
if DEBUG:
    MIN_INTERVAL = 10
    MAX_INTERVAL = 20

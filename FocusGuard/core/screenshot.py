"""截屏取证模块 - 在弹窗前自动截取当前屏幕作为证据"""
import os
from datetime import datetime
from PIL import ImageGrab

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREENSHOT_DIR


def take_screenshot() -> tuple:
    """截取当前屏幕，按日期归档保存。

    Returns:
        (filepath, PIL.Image): 截图路径和 PIL 图片对象
    """
    now = datetime.now()
    date_dir = os.path.join(SCREENSHOT_DIR, now.strftime("%Y-%m-%d"))
    os.makedirs(date_dir, exist_ok=True)

    filename = now.strftime("%H-%M-%S") + ".png"
    filepath = os.path.join(date_dir, filename)

    # all_screens=True 捕获所有显示器（多屏用户）
    try:
        img = ImageGrab.grab(all_screens=True)
    except Exception:
        # 部分系统不支持 all_screens，回退到主屏
        img = ImageGrab.grab()

    img.save(filepath, "PNG")
    return filepath, img

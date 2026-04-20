import os
import sys
from PIL import Image

# 模拟 tray.py 的路径逻辑
BASE_DIR = r"C:\Users\59669\Desktop\FocusGuard"
ICON_PATH = os.path.join(BASE_DIR, "assets", "icon.ico")

def test_icon_loading():
    print(f"[测试] 正在验证图标路径: {ICON_PATH}")
    if not os.path.exists(ICON_PATH):
        print("[错误] 图标文件不存在！")
        return False
    
    try:
        img = Image.open(ICON_PATH)
        print(f"[成功] 图标加载成功: {img.format}, {img.size}")
        return True
    except Exception as e:
        print(f"[错误] 图标加载失败: {e}")
        return False

if __name__ == "__main__":
    if test_icon_loading():
        sys.exit(0)
    else:
        sys.exit(1)

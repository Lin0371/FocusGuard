"""快速测试弹窗中文适配 - 直接触发一次完整的截屏+弹窗+日志流程"""
import sys
import os
import io

# 修复 Windows GBK 终端
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import tkinter as tk
from config import DATA_DIR, SCREENSHOT_DIR
from core.screenshot import take_screenshot
from core.popup import ReviewPopup
from core.logger import log_review


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # 截屏
    print("[测试] 正在截取屏幕...")
    screenshot_path, screenshot_img = take_screenshot()
    print(f"[测试] 截图已保存: {screenshot_path}")

    # 弹窗
    root = tk.Tk()
    root.withdraw()

    submitted = [False]

    def on_submit(status, description):
        print(f"[测试] 提交成功！")
        print(f"  状态: {status}")
        print(f"  描述: {description}")
        log_review(status, description, screenshot_path)
        print(f"[测试] 日志已写入: {os.path.join(DATA_DIR, 'review_log.md')}")
        submitted[0] = True
        root.after(500, root.destroy)

    popup = ReviewPopup(root, screenshot_path, screenshot_img, on_submit)
    popup.show()

    root.mainloop()

    if submitted[0]:
        # 验证日志文件中文编码
        log_path = os.path.join(DATA_DIR, "review_log.md")
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"\n[测试] 日志文件内容（最后 500 字符）:")
        print(content[-500:])
        print("\n[测试] ✅ 中文适配测试完成！")
    else:
        print("\n[测试] ⚠ 弹窗被关闭但未提交")


if __name__ == "__main__":
    main()

"""FocusGuard - 第一性原理防分心复盘守护程序

后台常驻，随机时间弹窗截屏拷问，强制你直面自己是否在推进核心目标。
"""
import sys
import os
import subprocess
import io

# 修复 Windows GBK 终端无法输出中文 emoji 的问题
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import tkinter as tk

# 确保 import 路径正确
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import DATA_DIR, SCREENSHOT_DIR, DEBUG
from core.timer import FocusTimer
from core.screenshot import take_screenshot
from core.popup import ReviewPopup
from core.logger import log_review
from core.tray import SystemTray


def ensure_background():
    """金蝉脱壳：如果当前是 python.exe 启动，自动切换到 pythonw.exe 并退出原进程。
    
    如果是打包后的 EXE，则跳过此逻辑。
    """
    if getattr(sys, 'frozen', False):
        return

    executable = os.path.basename(sys.executable).lower()
    if executable == "python.exe":
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if os.path.exists(pythonw):
            subprocess.Popen(
                [pythonw] + sys.argv,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                cwd=BASE_DIR,
            )
            sys.exit(0)


def main():
    # 生产模式：金蝉脱壳（调试时跳过，保留控制台输出）
    if not DEBUG:
        ensure_background()

    # 初始化数据目录
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # 创建隐藏的 Tk 主窗口（用于线程安全的 UI 调度）
    root = tk.Tk()
    root.withdraw()

    # 弹窗锁，防止定时器在弹窗期间重复触发
    popup_active = [False]

    def trigger_review():
        """定时器触发回调（在定时器线程中执行）。"""
        if popup_active[0]:
            return
        popup_active[0] = True

        # 先截屏（可以在非主线程执行）
        try:
            screenshot_path, screenshot_img = take_screenshot()
        except Exception as e:
            print(f"[FocusGuard] 截屏失败: {e}")
            popup_active[0] = False
            return

        # 通过 root.after() 在主线程中弹出 UI
        root.after(0, lambda: show_popup(screenshot_path, screenshot_img))

    def show_popup(screenshot_path, screenshot_img):
        """在主线程中创建复盘弹窗。"""
        def on_submit(status, description):
            log_review(status, description, screenshot_path)
            popup_active[0] = False
            if DEBUG:
                print(f"[FocusGuard] 已记录: {status} - {description}")

        popup = ReviewPopup(root, screenshot_path, screenshot_img, on_submit)
        popup.show()

    def on_exit():
        """退出程序。"""
        timer.stop()
        root.after(0, root.destroy)

    # 启动随机定时器
    timer = FocusTimer(trigger_review)
    timer.start()

    if DEBUG:
        from config import MIN_INTERVAL, MAX_INTERVAL
        print(f"[FocusGuard] 调试模式启动 | 间隔: {MIN_INTERVAL}~{MAX_INTERVAL} 秒")
        remaining = timer.get_remaining()
        print(f"[FocusGuard] 首次触发约 {int(remaining)} 秒后")

    # 启动系统托盘
    tray = SystemTray(timer, on_exit)
    tray.start()

    if not DEBUG:
        print("[FocusGuard] 守护程序已启动，最小化到系统托盘。")

    # 主线程进入 Tk 事件循环
    root.mainloop()


if __name__ == "__main__":
    main()

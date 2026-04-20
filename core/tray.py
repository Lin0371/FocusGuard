"""系统托盘管理 - 最小化常驻右下角"""
import threading
import os
import subprocess

from PIL import Image, ImageDraw
import pystray

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOG_FILE, ICON_PATH


def create_icon_image():
    """程序化生成托盘图标 - 紫色圆底 + 白色眼睛（监视意味）"""
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 紫色圆底
    draw.ellipse([2, 2, 62, 62], fill='#6366f1', outline='#818cf8', width=2)

    # 眼睛外轮廓（菱形/眼形）
    eye_points = [(12, 32), (32, 18), (52, 32), (32, 46)]
    draw.polygon(eye_points, fill='#e8e8f0')

    # 虹膜
    draw.ellipse([24, 24, 40, 40], fill='#16162a')

    # 瞳孔高光
    draw.ellipse([29, 28, 35, 34], fill='#e8e8f0')

    return img


class SystemTray:
    """系统托盘管理器。

    在右下角显示图标，右键菜单提供：休眠、查看记录、退出。
    """

    def __init__(self, timer, on_exit):
        """
        Args:
            timer: FocusTimer 实例
            on_exit: 退出时的回调函数
        """
        self.timer = timer
        self.on_exit = on_exit
        self._icon = None

    def start(self):
        """启动托盘图标。优先尝试从 assets/icon.ico 加载物理文件。"""
        if os.path.exists(ICON_PATH):
            try:
                icon_img = Image.open(ICON_PATH)
            except Exception:
                icon_img = create_icon_image()
        else:
            icon_img = create_icon_image()

        menu = pystray.Menu(
            pystray.MenuItem(
                lambda _: self._get_status_text(),
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("休眠 30 分钟", self._pause_30),
            pystray.MenuItem("休眠 1 小时", self._pause_60),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("查看今日记录", self._open_log),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出 FocusGuard", self._exit),
        )

        self._icon = pystray.Icon(
            "FocusGuard",
            icon_img,
            "FocusGuard - 专注守护",
            menu,
        )

        thread = threading.Thread(
            target=self._icon.run, daemon=True, name="SystemTray"
        )
        thread.start()

    def stop(self):
        """停止托盘。"""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _get_status_text(self):
        """动态显示下次提醒的大致时间。"""
        remaining = self.timer.get_remaining()
        if remaining <= 0:
            return "即将触发..."
        minutes = int(remaining / 60)
        if minutes < 1:
            return "不到 1 分钟后提醒"
        return f"约 {minutes} 分钟后提醒"

    def _pause_30(self, icon, item):
        self.timer.pause(30 * 60)

    def _pause_60(self, icon, item):
        self.timer.pause(60 * 60)

    def _open_log(self, icon, item):
        """用系统默认编辑器打开日志文件。"""
        if os.path.exists(LOG_FILE):
            os.startfile(LOG_FILE)
        else:
            # 日志还没创建，先创建空文件
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("# FocusGuard 复盘日志\n\n")
            os.startfile(LOG_FILE)

    def _exit(self, icon, item):
        """退出程序。"""
        self.stop()
        self.on_exit()

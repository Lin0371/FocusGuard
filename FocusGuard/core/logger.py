"""复盘日志写入模块 - 追加到 Markdown 文件"""
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOG_FILE, DATA_DIR

STATUS_EMOJI = {
    "正轨": "🟢",
    "偏离": "🟡",
    "摸鱼": "🔴",
}


def log_review(status: str, description: str, screenshot_path: str):
    """将复盘记录追加到 Markdown 日志文件。

    Args:
        status: "正轨" | "偏离" | "摸鱼"
        description: 用户输入的一句话说明
        screenshot_path: 对应截图的绝对路径
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    emoji = STATUS_EMOJI.get(status, "⚪")

    # 检查日志文件中是否已有今天的日期标题
    need_date_header = True
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if f"## {date_str}" in content:
                need_date_header = False

    # 截图相对路径（相对于日志文件所在目录）
    log_dir = os.path.dirname(LOG_FILE)
    try:
        rel_screenshot = os.path.relpath(screenshot_path, log_dir)
    except ValueError:
        rel_screenshot = screenshot_path

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if need_date_header:
            f.write(f"\n## {date_str}\n\n")
        f.write(f"### {time_str} {emoji} {status}\n")
        f.write(f"- **自述**: {description}\n")
        f.write(f"- **截图**: [查看]({rel_screenshot})\n\n")

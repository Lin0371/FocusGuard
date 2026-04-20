"""薛定谔定时器 - 不可预测的随机触发，基于绝对系统时间"""
import time
import random
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MIN_INTERVAL, MAX_INTERVAL


class FocusTimer:
    """基于 time.time() 绝对时间的随机定时器。

    防止 sleep 累计误差和系统休眠漂移。
    """

    def __init__(self, on_trigger):
        """
        Args:
            on_trigger: 到点时调用的回调函数（在定时器线程中执行）
        """
        self.on_trigger = on_trigger
        self._running = False
        self._paused_until = 0.0
        self._next_trigger_time = 0.0
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        """启动定时器后台线程。"""
        self._running = True
        self._schedule_next()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="FocusTimer"
        )
        self._thread.start()

    def stop(self):
        """停止定时器。"""
        self._running = False

    def pause(self, seconds: int):
        """暂停指定秒数（用于托盘菜单的休眠功能）。"""
        with self._lock:
            self._paused_until = time.time() + seconds
            self._schedule_next()

    def get_remaining(self) -> float:
        """获取距离下次触发的剩余秒数。"""
        with self._lock:
            remaining = self._next_trigger_time - time.time()
            return max(0.0, remaining)

    def _schedule_next(self):
        """随机生成下一次触发时间点（绝对时间戳）。"""
        now = time.time()
        base = max(now, self._paused_until)
        interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        self._next_trigger_time = base + interval

    def _loop(self):
        """主循环：每秒用 time.time() 检查是否到达触发时间。"""
        while self._running:
            now = time.time()
            with self._lock:
                should_trigger = (
                    now >= self._next_trigger_time
                    and now >= self._paused_until
                )

            if should_trigger:
                try:
                    self.on_trigger()
                except Exception as e:
                    print(f"[FocusTimer] 触发回调异常: {e}")
                with self._lock:
                    self._schedule_next()

            time.sleep(1)

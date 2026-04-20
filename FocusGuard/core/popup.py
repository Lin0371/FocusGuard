"""强制拷问弹窗 UI - 全屏暗幕 + 居中卡片 + 截图证据 + 状态选择 + 强制输入"""
import tkinter as tk
from PIL import Image, ImageTk

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MIN_INPUT_LENGTH


# ========== 配色方案 ==========
COLORS = {
    'overlay': '#0a0a12',       # 全屏暗幕
    'card': '#16162a',          # 卡片背景
    'card_border': '#2a2a4a',   # 卡片边框
    'text': '#e8e8f0',          # 主文字
    'text_dim': '#7878a0',      # 次要文字
    'accent': '#ff6b6b',        # 警告色（标题）
    'green': '#4ade80',         # 正轨
    'green_bg': '#162e1e',      # 正轨按钮背景
    'green_active': '#1a4a26',  # 正轨选中
    'yellow': '#facc15',        # 偏离
    'yellow_bg': '#2e2a16',     # 偏离按钮背景
    'yellow_active': '#4a4216', # 偏离选中
    'red': '#f87171',           # 摸鱼
    'red_bg': '#2e1616',        # 摸鱼按钮背景
    'red_active': '#4a1a1a',    # 摸鱼选中
    'input_bg': '#1e1e38',      # 输入框背景
    'input_border': '#3a3a5c',  # 输入框边框
    'btn_active': '#6366f1',    # 提交按钮可用
    'btn_hover': '#818cf8',     # 提交按钮悬停
    'btn_disabled': '#2a2a40',  # 提交按钮禁用
}

# 字体回退链
FONT_FAMILY = "Microsoft YaHei UI"


class ReviewPopup:
    """强制复盘弹窗。

    全屏暗幕覆盖 + 居中内容卡片。
    必须选择状态并输入描述才能关闭，无法绕过。
    """

    def __init__(self, master, screenshot_path, screenshot_img, on_submit):
        """
        Args:
            master: Tk 根窗口
            screenshot_path: 截图文件路径
            screenshot_img: PIL.Image 对象
            on_submit: 回调函数 (status, description) -> None
        """
        self.master = master
        self.screenshot_path = screenshot_path
        self.screenshot_img = screenshot_img
        self.on_submit = on_submit
        self.selected_status = None
        self._photo = None  # 防止 GC 回收

    def show(self):
        """创建并显示弹窗。"""
        C = COLORS

        # ===== 全屏暗幕窗口 =====
        self.window = tk.Toplevel(self.master)
        win = self.window
        win.overrideredirect(True)
        win.attributes('-topmost', True)

        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        win.geometry(f"{screen_w}x{screen_h}+0+0")
        win.configure(bg=C['overlay'])

        # 禁用 Alt+F4
        win.protocol("WM_DELETE_WINDOW", lambda: None)
        # 拦截 Escape
        win.bind('<Escape>', lambda e: None)

        # ===== 居中卡片容器 =====
        card_w = min(640, int(screen_w * 0.45))

        # 外层居中
        outer = tk.Frame(win, bg=C['overlay'])
        outer.place(relx=0.5, rely=0.5, anchor='center')

        # 卡片边框层
        border_frame = tk.Frame(outer, bg=C['card_border'], padx=1, pady=1)
        border_frame.pack()

        # 卡片内容层
        card = tk.Frame(border_frame, bg=C['card'], padx=35, pady=25, width=card_w)
        card.pack()
        card.pack_propagate(False)
        card.configure(width=card_w)

        # ===== 顶部警告标识 =====
        warning_bar = tk.Frame(card, bg=C['accent'], height=3)
        warning_bar.pack(fill='x', pady=(0, 20))

        # ===== 标题 =====
        header = tk.Label(
            card,
            text="⚠  停。复盘时间到。",
            font=(FONT_FAMILY, 18, "bold"),
            fg=C['accent'],
            bg=C['card'],
        )
        header.pack(anchor='w', pady=(0, 5))

        sub_header = tk.Label(
            card,
            text="下面是你刚才的屏幕，说实话。",
            font=(FONT_FAMILY, 10),
            fg=C['text_dim'],
            bg=C['card'],
        )
        sub_header.pack(anchor='w', pady=(0, 15))

        # ===== 截图证据 =====
        img_outer = tk.Frame(card, bg=C['input_border'], padx=1, pady=1)
        img_outer.pack(fill='x', pady=(0, 18))

        # 生成缩略图
        thumb_w = card_w - 75
        thumb_h = int(thumb_w * 0.45)
        thumb = self.screenshot_img.copy()
        thumb.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(thumb)

        img_label = tk.Label(img_outer, image=self._photo, bg=C['card'])
        img_label.pack()

        # ===== 拷问文字 =====
        question = tk.Label(
            card,
            text="你现在做的事，是在推进核心目标，还是在瞎折腾？",
            font=(FONT_FAMILY, 11),
            fg=C['text'],
            bg=C['card'],
            wraplength=card_w - 80,
            justify='left',
        )
        question.pack(anchor='w', pady=(0, 15))

        # ===== 状态选择按钮组 =====
        status_label = tk.Label(
            card,
            text="当前状态",
            font=(FONT_FAMILY, 9),
            fg=C['text_dim'],
            bg=C['card'],
        )
        status_label.pack(anchor='w', pady=(0, 6))

        status_frame = tk.Frame(card, bg=C['card'])
        status_frame.pack(fill='x', pady=(0, 18))

        self._status_buttons = {}
        statuses = [
            ("🟢  正轨", "正轨", C['green'], C['green_bg'], C['green_active']),
            ("🟡  偏离", "偏离", C['yellow'], C['yellow_bg'], C['yellow_active']),
            ("🔴  摸鱼", "摸鱼", C['red'], C['red_bg'], C['red_active']),
        ]

        for text, value, fg_color, bg_normal, bg_selected in statuses:
            btn = tk.Button(
                status_frame,
                text=text,
                font=(FONT_FAMILY, 10),
                fg=fg_color,
                bg=bg_normal,
                activeforeground=fg_color,
                activebackground=bg_selected,
                relief='flat',
                bd=0,
                padx=10,
                pady=8,
                cursor='hand2',
                command=lambda v=value: self._select_status(v),
            )
            btn.pack(side='left', expand=True, fill='x', padx=(0, 6))
            self._status_buttons[value] = (btn, fg_color, bg_normal, bg_selected)

        # ===== 文字输入 =====
        input_label = tk.Label(
            card,
            text="一句话说明你在干嘛：",
            font=(FONT_FAMILY, 9),
            fg=C['text_dim'],
            bg=C['card'],
        )
        input_label.pack(anchor='w', pady=(0, 6))

        input_frame = tk.Frame(card, bg=C['input_border'], padx=1, pady=1)
        input_frame.pack(fill='x', pady=(0, 20))

        self._input = tk.Entry(
            input_frame,
            font=(FONT_FAMILY, 11),
            fg=C['text'],
            bg=C['input_bg'],
            insertbackground=C['text'],
            relief='flat',
            bd=0,
        )
        self._input.pack(fill='x', ipady=10, padx=8, pady=4)
        self._input.bind('<KeyRelease>', lambda e: self._check_submit())
        self._input.bind('<Return>', lambda e: self._try_submit())

        # ===== 提交按钮 =====
        self._submit_btn = tk.Button(
            card,
            text="提交复盘",
            font=(FONT_FAMILY, 12, "bold"),
            fg=C['text_dim'],
            bg=C['btn_disabled'],
            activeforeground=C['text'],
            activebackground=C['btn_active'],
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            state='disabled',
            cursor='',
            command=self._try_submit,
        )
        self._submit_btn.pack(fill='x', pady=(0, 5))

        # ===== 底部提示 =====
        hint = tk.Label(
            card,
            text=f"选择状态 + 输入至少 {MIN_INPUT_LENGTH} 个字才能提交",
            font=(FONT_FAMILY, 8),
            fg=C['text_dim'],
            bg=C['card'],
        )
        hint.pack(pady=(5, 0))

        # ===== 焦点抢占 =====
        win.after(100, win.focus_force)
        win.after(100, win.lift)
        win.after(150, win.focus_force)
        win.after(200, self._input.focus_set)

        # 让卡片自适应内容高度
        card.pack_propagate(True)

    def _select_status(self, status):
        """选择状态并更新按钮样式。"""
        C = COLORS
        self.selected_status = status

        for value, (btn, fg, bg_normal, bg_selected) in self._status_buttons.items():
            if value == status:
                btn.configure(bg=bg_selected, relief='flat')
            else:
                btn.configure(bg=bg_normal, relief='flat')

        self._check_submit()

    def _check_submit(self):
        """检查是否满足提交条件，更新按钮状态。"""
        C = COLORS
        text = self._input.get().strip()
        can_submit = self.selected_status and len(text) >= MIN_INPUT_LENGTH

        if can_submit:
            self._submit_btn.configure(
                state='normal',
                bg=C['btn_active'],
                fg=C['text'],
                cursor='hand2',
            )
            # 悬停效果
            self._submit_btn.bind('<Enter>',
                lambda e: self._submit_btn.configure(bg=C['btn_hover']))
            self._submit_btn.bind('<Leave>',
                lambda e: self._submit_btn.configure(bg=C['btn_active']))
        else:
            self._submit_btn.configure(
                state='disabled',
                bg=C['btn_disabled'],
                fg=C['text_dim'],
                cursor='',
            )
            self._submit_btn.unbind('<Enter>')
            self._submit_btn.unbind('<Leave>')

    def _try_submit(self):
        """尝试提交，条件不满足时不做任何事。"""
        text = self._input.get().strip()
        if not self.selected_status or len(text) < MIN_INPUT_LENGTH:
            return

        # 回调
        self.on_submit(self.selected_status, text)
        # 销毁弹窗
        self.window.destroy()

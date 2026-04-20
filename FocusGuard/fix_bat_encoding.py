import os

# 定义路径
bat_path = r"C:\Users\59669\Desktop\FocusGuard\FocusGuard.bat"

# 使用 ANSI 编码写入极其简练的 ASCII 内容，彻底解决中文系统乱码问题
content = """@echo off
cd /d "%~dp0"
python main.py
exit
"""

with open(bat_path, "w", encoding="ansi") as f:
    f.write(content)

print(f"Done: {bat_path}")

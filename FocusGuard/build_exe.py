import subprocess
import sys
import os
import shutil

def run_command(command, cwd=None):
    print(f"执行命令: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"命令失败，退出码: {result.returncode}")
        return False
    return True

def main():
    # 1. 确保安装了 pyinstaller
    print("正在检查打包工具 PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        print("未检测到 PyInstaller，正在尝试安装...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
            print("安装失败，请手动执行 'pip install pyinstaller'")
            return

    # 2. 定位资源
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    
    if not os.path.exists(icon_path):
        print(f"警告: 未找到图标文件 {icon_path}，将不带图标打包。")
        icon_flag = []
    else:
        icon_flag = ["--icon", icon_path]

    # 3. 构建打包命令
    # --onefile: 打包成单个可执行文件
    # --noconsole: 运行时不显示黑色的命令行窗口
    # --add-data: 将 assets 文件夹打包进 EXE 内部 (Windows 格式: 文件夹;目标文件夹)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name", "FocusGuard",
        "--add-data", f"assets;assets",
    ] + icon_flag + ["main.py"]

    print("\n--- 开始打包 ---")
    if run_command(cmd, cwd=base_dir):
        print("\n[成功] 打包成功！")
        print(f"可执行文件位于: {os.path.join(base_dir, 'dist', 'FocusGuard.exe')}")
        print("\n提示: 你可以将 dist/FocusGuard.exe 分发给其他人使用。")
        print("注意: 第一次运行时，它会在同级目录下创建 data/ 文件夹。")
    else:
        print("\n[失败] 打包失败，请查看上方报错信息。")

if __name__ == "__main__":
    main()

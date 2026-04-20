import os
import sys
import subprocess
import shutil

# 配置
VENV_DIR = ".venv_build"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(BASE_DIR, "requirements.txt")
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")

# 要明确排除的大载重库，防止 PyInstaller 误抓
EXCLUDES = [
    "numpy", "matplotlib", "pandas", "scipy", "mkl", "toplevel",
    "IPython", "jupyter", "PIL.ImageQt", "PIL.ImageTk" # 我们只用纯 PIL 和 tkinter，不用结合部
]

def run(cmd, cwd=None, env=None):
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=False)
    if result.returncode != 0:
        print(f"失败，码: {result.returncode}")
        return False
    return True

def main():
    print("--- FocusGuard 极致瘦身打包流程 ---")
    
    # 1. 创建干净的虚拟环境
    if os.path.exists(VENV_DIR):
        print(f"清除旧的构建环境: {VENV_DIR}")
        shutil.rmtree(VENV_DIR)
        
    print(f"正在创建新的虚拟环境...")
    if not run([sys.executable, "-m", "venv", VENV_DIR]):
        return

    # 获取虚拟环境中的 python 和 pip 路径
    if sys.platform == "win32":
        venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")
        venv_pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(VENV_DIR, "bin", "python")
        venv_pip = os.path.join(VENV_DIR, "bin", "pip")

    # 2. 在虚拟环境中安装最小依赖
    print("正在虚拟环境中安装最小依赖...")
    if not run([venv_python, "-m", "pip", "install", "--upgrade", "pip"]):
        return
    if not run([venv_python, "-m", "pip", "install", "-r", REQ_FILE]):
        return

    # 3. 执行打包
    print("正在以最小环境执行打包...")
    
    # 手动拼接排除参数
    exclude_args = []
    for mod in EXCLUDES:
        exclude_args.extend(["--exclude-module", mod])

    icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
    icon_args = ["--icon", icon_path] if os.path.exists(icon_path) else []

    # 使用 venv 里的 pyinstaller
    # 注意：pyinstaller 必须也在 venv 里装了才能直接通过 python -m 跑
    cmd = [
        venv_python, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name", "FocusGuard_compact",
        "--add-data", "assets;assets"
    ] + exclude_args + icon_args + ["main.py"]

    if run(cmd, cwd=BASE_DIR):
        print("\n[成功] 极致打包完成！")
        exe_path = os.path.join(DIST_DIR, "FocusGuard_compact.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"最终体积: {size_mb:.2f} MB")
            print(f"文件位置: {exe_path}")
            print("\n你现在可以删除 .venv_build, build 文件夹以及 .spec 文件了。")
    else:
        print("\n[失败] 打包过程中出现错误。")

if __name__ == "__main__":
    main()

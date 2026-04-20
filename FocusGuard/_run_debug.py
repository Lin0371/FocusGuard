import subprocess
import sys

def run():
    result = subprocess.run(
        [sys.executable, r'C:\Users\59669\Desktop\FocusGuard\main.py'],
        check=False,
    )
    return result.returncode

if __name__ == "__main__":
    sys.exit(run())

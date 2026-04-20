import subprocess
import sys
import os

def run():
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-r', req_file],
        check=False,
    )
    return result.returncode

if __name__ == "__main__":
    sys.exit(run())

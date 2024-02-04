import sys
import subprocess
import time

while True:
    print('Self-Bot running in process, please wait...')
    try:
        subprocess.call([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("Terminated")
        raise SystemExit
    time.sleep(0.1)
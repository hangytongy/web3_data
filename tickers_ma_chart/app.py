import time
import subprocess

if __name__ == "__main__":
    while True:
        subprocess.run(["python","main.py"])
        time.sleep(86400)

import subprocess
import time

while True:
    subprocess.run(
        ["python", "main.py"]
    )
    time.sleep(60*24*24)
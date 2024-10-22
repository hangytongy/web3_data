import time
import subprocess

def run_app():
    define_time = 60 * 10
    while True:
        subprocess.run(['python', 'main.py'])
        time.sleep(define_time)

if __name__ == "__main__":
    run_app()
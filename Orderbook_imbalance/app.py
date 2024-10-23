import time
import subprocess
import threading

def run_app():
    define_time = 60 * 10
    while True:
        subprocess.run(['python', 'main.py'])
        time.sleep(define_time)

def run_plot_data():
    while True:
        subprocess.run(['python', 'plot_data.py'])
        subprocess.run(['python', 'delete_data.py']) #deletes data from 5 days prior to today
        time.sleep(43200)


if __name__ == "__main__":
    app_thread = threading.Thread(target=run_app)
    plot_thread = threading.Thread(target=run_plot_data)

    app_thread.start()
    plot_thread.start()

    app_thread.join()
    plot_thread.join()
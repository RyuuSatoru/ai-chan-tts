import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadBotHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(['python', self.script])

    def restart_bot(self):
        print("Có cập nhật mới từ Source Code, đang bắt đầu khởi động lại...")
        self.start_bot()

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            self.restart_bot()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data/watch.py <path_to_bot_script>")
        sys.exit(1)

    path = sys.argv[1]
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        print(f"Error: The path {abs_path} does not exist.")
        sys.exit(1)

    event_handler = ReloadBotHandler(abs_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(abs_path), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
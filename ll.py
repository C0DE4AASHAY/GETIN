# reloader.py
import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_EXTENSIONS = ['.py']
EXCLUDE_DIRS = ['__pycache__']

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process_starter):
        super().__init__()
        self.restart_process = process_starter

    def on_modified(self, event):
        if any(event.src_path.endswith(ext) for ext in WATCHED_EXTENSIONS):
            if not any(excluded in event.src_path for excluded in EXCLUDE_DIRS):
                print(f"🔄 Detected change in: {event.src_path}")
                self.restart_process()

def start_bot():
    return subprocess.Popen([sys.executable, 'main.py'])

def main():
    bot_process = start_bot()

    def restart():
        nonlocal bot_process
        if bot_process:
            bot_process.kill()
            print("🔁 Restarting bot...")
        bot_process = start_bot()

    event_handler = ReloadHandler(restart)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    print("👀 Watching for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher and bot...")
        bot_process.kill()
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

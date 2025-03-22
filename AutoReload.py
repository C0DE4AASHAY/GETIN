import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, bot_process):
        self.bot_process = bot_process

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("🔄 Code changed! Restarting bot...")
            
            # Stop the current bot process
            self.bot_process.terminate()
            self.bot_process.wait()  # Ensure process fully stops
            
            time.sleep(1)  # Short delay before restarting
            
            # Restart the bot
            self.bot_process = subprocess.Popen(["python", "main.py"])

def start_bot():
    bot_process = subprocess.Popen(["python", "main.py"])
    event_handler = ReloadHandler(bot_process)
    
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        bot_process.terminate()
        bot_process.wait()  # Ensure process fully stops

    observer.join()

if __name__ == "__main__":
    start_bot()


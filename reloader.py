import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Repo
# https://github.com/junaidmgithub/autoreloader

# Installation
# >>> pip install watchdog

EXECUTABLE = "python3" # node/python
FILE_PATH = "test/main.py" # Replace with your source file
WATCH_FILE_EXTENTIONS = [".py", ".html", ".css", ".txt", ".js", ".jsx", ".sql", ".sh", ".ts", ".env", ".json", ".yaml"]
SKIP_FILE_EXTENTIONS = []

class FileChangeReloader(FileSystemEventHandler):
    
    def __init__(self, executable, script_path, watch_extentions, skip_extentions):
        super().__init__()
        self.executable = executable
        self.script_path = script_path
        self.watch_extentions = watch_extentions
        self.skip_extentions = skip_extentions
        self.thread = None
        self.last_modified = None
        # Start script
        self.restart_thread()

    def on_modified(self, event):
        
        if event.is_directory:
            return

        file_path = event.src_path
        if any(file_path.endswith(ext) for ext in self.watch_extentions):
            if any(file_path.endswith(ext) for ext in self.skip_extentions):
                return # skip
            current_time = time.time()
            if self.last_modified is None or current_time - self.last_modified > 1:
                self.last_modified = current_time
                print(f"Detected change in {file_path}. Reloading...")
                self.restart_thread()

    def restart_thread(self):
        
        if self.thread and self.thread.is_alive():
            self.thread.cancel()

        self.thread = threading.Thread(target=self.run_script)
        self.thread.start()

    def run_script(self):
        try:
            os.system(f"{self.executable} {self.script_path}")
        except Exception as e:
            print(f"Error running {self.script_path}: {e}")


def start_reloader(executable, path, watch_extentions, skip_extentions):

    script_path = os.path.abspath(path)  
    event_handler = FileChangeReloader(executable, script_path, watch_extentions, skip_extentions)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(script_path), recursive=True)
    observer.start()
    
    # To prevent exit reloader.py script 
    try:
        print(f"Watching directory {os.path.dirname(script_path)} for changes...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


start_reloader(EXECUTABLE, FILE_PATH, WATCH_FILE_EXTENTIONS, SKIP_FILE_EXTENTIONS)

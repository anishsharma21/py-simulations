import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import DirModifiedEvent, FileModifiedEvent

class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self._modified = False

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        if str(event.src_path).endswith(".py"):
            print(f"Detected change in {event.src_path}. Marking for restart.")
            self._modified = True
    
    def is_modified(self):
        return self._modified

def watch_for_changes():
    event_handler = RestartHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    return observer, event_handler

def restart_program():
    """Restarts the current program."""
    print("Restarting program...")
    python = sys.executable
    os.execl(python, python, *sys.argv)
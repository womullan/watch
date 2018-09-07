import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.utils import unicode_paths
from pathtools.patterns import match_any_paths
from astropy.io import fits

class Watcher:
    DIRECTORY_TO_WATCH = "."

    def __init__(self,dirName="."):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = dirName
        print("Monitoring - %s."% self.DIRECTORY_TO_WATCH)


    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s."% event.src_path)


if __name__ == '__main__':
    w = Watcher(sys.argv[1])
    w.run()

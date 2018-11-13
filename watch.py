import sys
import time
import os
import glob
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileCreatedEvent
from watchdog.utils import unicode_paths
from pathtools.patterns import match_any_paths
from astropy.io import fits


class Watcher:
    # Class to watch files in a directory using watchdog.
    #You can use this on a command line in a terminal it just outputs file created.
    DIRECTORY_TO_WATCH = "."
    event_handler = None
    usels = True
    last_file = ""

    def __init__(self,dirName=".",ls=True):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = dirName
        self.usels = ls
        self.event_handler=Handler()

        if (self.usels):
            print("Using ls to raise event." )
        print("Monitoring - %s."% os.path.abspath(self.DIRECTORY_TO_WATCH))


    def run(self):
        if self.usels == 0:
           print("Regestering handler - %s." % self.event_handler)
           self.observer.schedule(self.event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
           self.observer.start()
        try:
            while True:
                time.sleep(5)
                if (self.usels) :
                   try:
                      self.checkNew()
                   except Exception as e:
                      print(e)
        except Exception as ex:
            if self.usels == 0:
                self.observer.stop()
            print(ex)

        if self.usels == 0:
           self.observer.join()

    def checkNew(self):
        list_of_files = glob.glob(os.path.abspath(self.DIRECTORY_TO_WATCH)+'/*fit*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        if (self.last_file != latest_file) :
            self.last_file = latest_file
            #print("New file - %s." % self.last_file)
            event = FileCreatedEvent(self.last_file)
            self.event_handler.on_any_event(event)


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)





class FitsWatcher(Watcher):
    #Class to watch for FITS files ina  adirectory.
    #This will try to render the nth file - so if its not in a notebook it will not work.
    NUM_TO_SKIP = 0

    def __init__(self,dirName=".",numToSkip=2):
        super().__init__(dirName)
        self.NUM_TO_SKIP=numToSkip
        self.event_handler=FitsHandler(self.NUM_TO_SKIP)
        print("will render each %d."% (self.NUM_TO_SKIP))


class FitsHandler(FileSystemEventHandler):
    COUNT=0
    NUM_TO_SKIP=0

    def __init__(self,skip):
        FitsHandler.COUNT=0
        FitsHandler.NUM_TO_SKIP=skip

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
        # Count fits files and render some of them ..
            print("Received - %s." % event.src_path)
            if (event.src_path.endswith(".fits") or event.src_path.endswith(".fits.gz") ):
                FitsHandler.COUNT = FitsHandler.COUNT + 1
                if (FitsHandler.COUNT % FitsHandler.NUM_TO_SKIP == 0):
                    FitsHandler.render(event.src_path)
            else:
                print("Skipping - %s." % event.src_path)


    @staticmethod
    def render(filePath):
        print("Rendering - %s." % filePath)
        try:
            image_data = fits.getdata(filePath)
            plt.rcParams['figure.figsize'] = [10, 10]
            plt.imshow(image_data, cmap='gray')
            plt.colorbar()
            plt.show()
        except Exception as  ex:
            print("Can not load fits - %s." % ex)



if __name__ == '__main__':
    w = Watcher(sys.argv[1])
    w.run()


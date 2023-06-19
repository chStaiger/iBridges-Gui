"""Continuous upload tools

"""
import logging
from queue import Queue
from threading import Thread
from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

import utils

new_files_queue = Queue()


# Callback for file creation and manipulation, this thread stores all file creations in a queue.
class FileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if "." in event.src_path: # Ignore folders
            new_files_queue.put(event.src_path)


# Reference to the assync running filesystem event observer
class FileWatcher():
    def __init__(self, directory):
        event_handler = FileEventHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, path = directory, recursive = True)
        self.observer.start()

    def stop(self):
        if self.observer.isAlive():
            self.observer.stop()
            self.observer.join()


# Continous upload thread
class contUpload(Thread):
    def __init__(self, source, destColl, upload_mode ="all", r_local_copy = False):
        self.tosync_dictionary = {}
        self.fWatcher = FileWatcher(source)
        self._running = True
        self.destColl = destColl
        self.upload_mode = upload_mode
        self.r_local_copy = r_local_copy
        self.force = self.conf.get('force_transfers', False)
        Thread.__init__(self)


    # Upload new files when criterea is met. 
    def run(self):
        while self._running == True:
            new_file = new_files_queue.get()
            if self.upload_mode == "meta":
                # Store files until metadata file appears, than upload. 
                filepath, filename = path.split(new_file)
                if filename == "metadata.json":
                    if filepath in self.tosync_dictionary:
                        folder_wfiles = self.tosync_dictionary.pop(filepath)
                        self.conn.upload_data(filepath, self.destColl, None, None, force=self.force)
                    else:
                        logging.debug("Something's going wrong. data folder in %s not tracked", filepath)
                else: # Add files with folder as key
                    pathparts =  filepath.rsplit(path.sep, 1)
                    if pathparts[1] == "Data":
                        if pathparts[0] in self.tosync_dictionary:
                            self.tosync_dictionary[pathparts[0]].append(pathparts[1] + path.sep + filename) 
                        else:
                            self.tosync_dictionary[pathparts[0]] = [pathparts[1] + path.sep + filename]
                    else:
                        logging.debug('TODO, this should not happen? %s  %s', filepath, filename)
            elif self.upload_mode == "f500":
                logging.debug('TODO figure out how to do the F500 upload')

            else: # "all"
                self.conn.upload_data(new_file, self.destColl, None, None, force=self.force)

        # Stop file watcher
        self.fWatcher.stop()

    def stop(self):
        self._running = False





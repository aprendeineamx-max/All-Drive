import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread, Lock
import queue

class FileWatcher(FileSystemEventHandler):
    def __init__(self, s3_handler, bucket_name, watch_dir, callback=None):
        self.s3_handler = s3_handler
        self.bucket_name = bucket_name
        self.watch_dir = watch_dir
        self.callback = callback
        self.upload_queue = queue.Queue()
        self.lock = Lock()
        self.running = False
        self.upload_thread = None

    def on_created(self, event):
        if not event.is_directory:
            self._queue_upload(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            self._queue_upload(event.src_path, "modified")

    def _queue_upload(self, file_path, action):
        """Add file to upload queue"""
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.upload_queue.put((file_path, action))
            if self.callback:
                self.callback(f"Detected {action}: {os.path.basename(file_path)}")

    def _upload_worker(self):
        """Worker thread to process upload queue"""
        while self.running:
            try:
                file_path, action = self.upload_queue.get(timeout=1)
                
                # Wait a bit to ensure file is fully written
                time.sleep(2)
                
                if os.path.exists(file_path):
                    relative_path = os.path.relpath(file_path, self.watch_dir)
                    
                    if self.callback:
                        self.callback(f"Uploading: {relative_path}")
                    
                    success = self.s3_handler.upload_file(
                        self.bucket_name, 
                        file_path, 
                        relative_path
                    )
                    
                    if success and self.callback:
                        self.callback(f"✓ Uploaded: {relative_path}")
                    elif self.callback:
                        self.callback(f"✗ Failed: {relative_path}")
                
                self.upload_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.callback:
                    self.callback(f"Error: {str(e)}")

    def start_monitoring(self):
        """Start the file monitoring"""
        self.running = True
        self.upload_thread = Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()

    def stop_monitoring(self):
        """Stop the file monitoring"""
        self.running = False
        if self.upload_thread:
            self.upload_thread.join(timeout=5)


class RealTimeSync:
    def __init__(self, s3_handler, bucket_name, watch_directory, callback=None):
        self.s3_handler = s3_handler
        self.bucket_name = bucket_name
        self.watch_directory = watch_directory
        self.callback = callback
        self.observer = None
        self.event_handler = None

    def start(self):
        """Start real-time synchronization"""
        if self.observer and self.observer.is_alive():
            return False, "Already running"

        try:
            self.event_handler = FileWatcher(
                self.s3_handler,
                self.bucket_name,
                self.watch_directory,
                self.callback
            )
            
            self.event_handler.start_monitoring()
            
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.watch_directory,
                recursive=True
            )
            self.observer.start()
            
            return True, f"Monitoring started for {self.watch_directory}"
        except Exception as e:
            return False, f"Error starting monitor: {str(e)}"

    def stop(self):
        """Stop real-time synchronization"""
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=5)
                
                if self.event_handler:
                    self.event_handler.stop_monitoring()
                
                return True, "Monitoring stopped"
            except Exception as e:
                return False, f"Error stopping monitor: {str(e)}"
        return False, "Not running"

    def is_running(self):
        """Check if monitoring is active"""
        return self.observer and self.observer.is_alive()

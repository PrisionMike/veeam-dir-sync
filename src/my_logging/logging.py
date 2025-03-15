from datetime import datetime

class MyLogger:
    def __init__(self, sync_log_file, io_log_file):
        self.sync_log_file = sync_log_file
        self.io_log_file = io_log_file

    def log_file_updated(self, replica_file_path, file_hash):
        with open(self.io_log_file, 'a') as f:
            f.write(f"[{datetime.now()}] --- FILE UPDATED --- {replica_file_path} --- {file_hash}\n")

    def log_file_created(self, replica_file_path, file_hash):
        with open(self.io_log_file, 'a') as f:
            f.write(f"[{datetime.now()}] --- FILE CREATED --- {replica_file_path} --- {file_hash}\n")
        
    def log_dir_created(self, replica_subdir):
        with open(self.io_log_file, 'a') as f:
            f.write(f"[{datetime.now()}] --- DIR CREATED  --- {replica_subdir}\n")

    def log_dir_removed(self, full_path):
        with open(self.io_log_file, 'a') as f:
            f.write(f"[{datetime.now()}] --- DIR REMOVED  --- {full_path}\n")

    def log_file_removed(self, full_path):
        with open(self.io_log_file, 'a') as f:
            f.write(f"[{datetime.now()}] --- FILE REMOVED --- {full_path}\n")

    def log_sync(self, file_hash = None):
        with open(self.sync_log_file, 'a') as f:
            f.write(f"--- SYNCED AT --- [{datetime.now()}]")
            if file_hash:
                f.write(f" --- {file_hash}")
            f.write(f"\n")

    def clear_io_logs(self):
        open(self.io_log_file,'w').close()

    def clear_sync_logs(self):
        open(self.sync_log_file,'w').close()
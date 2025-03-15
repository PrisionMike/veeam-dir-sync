from datetime import datetime

def log_file_updated(replica_file_path, file_hash, log_file):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] --- FILE UPDATED --- {replica_file_path} --- {file_hash}\n")

def log_file_created(replica_file_path, file_hash, log_file):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] --- FILE CREATED --- {replica_file_path} --- {file_hash}\n")
    
def log_dir_created(replica_subdir, log_file):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] --- DIR CREATED  --- {replica_subdir}\n")

def log_dir_removed(full_path, log_file):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] --- DIR REMOVED  --- {full_path}\n")

def log_file_removed(full_path, log_file):
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now()}] --- FILE REMOVED --- {full_path}\n")

def log_sync(sync_log_file):
    with open(sync_log_file, 'a') as f:
        f.write(f"--- SYNCED AT --- [{datetime.now()}]\n")

def clear_logs(log_file):
    open(log_file,'w').close()
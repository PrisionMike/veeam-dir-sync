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
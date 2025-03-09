import shutil
from os import path, makedirs

def sync_file(source_path, replica_path, dirpath, filename, file_hash):
    rel_path = path.relpath(dirpath, source_path)
    replica_dir = path.join(replica_path, rel_path)
    if not path.exists(replica_dir):
        makedirs(replica_dir, exist_ok=True)
    source_file_path = path.join(dirpath, filename)
    replica_file_path = path.join(replica_dir, filename)
    if not path.exists(replica_file_path):
        shutil.copy2(source_file_path, replica_file_path)
        log_file_created(replica_file_path, file_hash)
    else:
        replica_file_hash = md5_file(replica_file_path)
        if replica_file_hash != file_hash:
            shutil.copy2(source_file_path, replica_file_path)
            log_file_updated(replica_file_path, file_hash)
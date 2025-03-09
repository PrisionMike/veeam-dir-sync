import os
import hashlib
import shutil
from dotenv import load_dotenv

SOURCE_DIR = None
REPLICA_DIR = None
ROOT_DIR = None
IO_LOG_FILE = None

def populate_globals():
    global SOURCE_DIR
    global ROOT_DIR
    global REPLICA_DIR
    global IO_LOG_FILE
    
    load_dotenv('/home/strider/veeam-assignment/.env')
    
    ROOT_DIR = os.getenv("ROOT_DIR")
    SOURCE_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("SOURCE_DIR")))
    REPLICA_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("REPLICA_DIR")))
    # SOURCE_DIR = os.getenv("SOURCE_DIR")
    # REPLICA_DIR = os.getenv("REPLICA_DIR")
    IO_LOG_FILE = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("IO_LOG_FILE")))


def md5_file(filepath):
    """Compute the MD5 hash of a file by reading it in chunks."""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()

def walk_the_dir(root):
    """
    Compute a full directory hash (Merkle tree style) using a DFS approach.
    This function uses os.walk with topdown=False (i.e. bottom-up)
    so that subdirectories are processed before their parents.
    """
    dir_hashes = {}
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        entries = []
        for filename in sorted(filenames):
            fullpath = os.path.join(dirpath, filename)
            file_hash = md5_file(fullpath)
            sync_file_with_replica(dirpath, filename, file_hash)
            entries.append(filename + file_hash)
            print("File hash:", file_hash)

        for dirname in sorted(dirnames):
            subdir_path = os.path.join(dirpath, dirname)
            sync_dir_with_replica(dirpath, dirname)
            if subdir_path in dir_hashes:
                entries.append(dirname + dir_hashes[subdir_path])

        combined = ''.join(entries).encode('utf-8')
        dir_hashes[dirpath] = hashlib.md5(combined).hexdigest()

    return dir_hashes[root]

def sync_file_with_replica(dirpath, filename, file_hash):
    rel_path = os.path.relpath(dirpath, SOURCE_DIR)
    replica_dir = os.path.join(REPLICA_DIR, rel_path)
    if not os.path.exists(replica_dir):
        os.makedirs(replica_dir, exist_ok=True)
    source_file_path = os.path.join(dirpath, filename)
    replica_file_path = os.path.join(replica_dir, filename)
    if not os.path.exists(replica_file_path):
        shutil.copy2(source_file_path, replica_file_path)
        log_file_created(replica_file_path)
    else:
        replica_file_hash = md5_file(replica_file_path)
        if replica_file_hash != file_hash:
            shutil.copy2(source_file_path, replica_file_path)
            log_file_updated(replica_file_path)

def log_file_updated(replica_file_path):
    print(f"Updated file: {replica_file_path}")

def log_file_created(replica_file_path):
    print(f"Copied new file: {replica_file_path}")
    
def sync_dir_with_replica(dirpath, dirname):
    rel_path = os.path.relpath(dirpath, SOURCE_DIR)
    replica_dir = os.path.join(REPLICA_DIR, rel_path)
    replica_subdir = os.path.join(replica_dir, dirname)
    if not os.path.exists(replica_subdir):
        os.makedirs(replica_subdir, exist_ok=True)
        print(f"Created replica directory: {replica_subdir}")

if __name__ == '__main__':
    populate_globals()
    full_hash = walk_the_dir(SOURCE_DIR)
    print("Full directory hash:", full_hash)

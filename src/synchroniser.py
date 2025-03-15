import os
import hashlib

from dotenv import load_dotenv

from utils.utils import md5_file
from my_logging.logging import MyLogger
from syncers.copiers import Synchroniser

SOURCE_DIR = None
REPLICA_DIR = None
ROOT_DIR = None
IO_LOG_FILE = None
SYNC_LOG_FILE = None

def populate_globals():
    global SOURCE_DIR
    global ROOT_DIR
    global REPLICA_DIR
    global IO_LOG_FILE
    global SYNC_LOG_FILE
    
    load_dotenv('/home/strider/veeam-assignment/.env', override=True)
    ROOT_DIR = os.getenv("ROOT_DIR")
    SOURCE_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("SOURCE_DIR")))
    REPLICA_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("REPLICA_DIR")))
    # SOURCE_DIR = os.getenv("SOURCE_DIR")
    # REPLICA_DIR = os.getenv("REPLICA_DIR")
    IO_LOG_FILE = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("IO_LOG_FILE")))
    SYNC_LOG_FILE = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("SYNC_LOG_FILE")))

def sync_the_dirs(syncer: Synchroniser):
    """
    Merkle tree hash. Only root hash is returned. Since we don't have a ready-to-use
    way to detect file changes deeper in the directory structure, the Merkle construction
    is moot. Thus this function IS SIMPLY A DFS traversal of the directory argument.
    """
    dir_hashes = {}
    for dirpath, dirnames, filenames in os.walk(syncer.source_path, topdown=False):
        entries = []

        for filename in sorted(filenames):
            fullpath = os.path.join(dirpath, filename)
            file_hash = md5_file(fullpath)
            syncer.sync_file(dirpath, filename, file_hash)
            entries.append(filename + file_hash)

        for dirname in sorted(dirnames):
            subdir_path = os.path.join(dirpath, dirname)
            syncer.sync_dir(dirpath, dirname) # For empty dirs.
            if subdir_path in dir_hashes:
                entries.append(dirname + dir_hashes[subdir_path])

        syncer.sync_prune(dirpath, dirnames, filenames)
        combined = ''.join(entries).encode('utf-8')
        dir_hashes[dirpath] = hashlib.md5(combined).hexdigest()

    syncer.my_logger.log_sync()
    return dir_hashes[syncer.source_path]

if __name__ == '__main__':
    populate_globals()
    my_logger = MyLogger(SYNC_LOG_FILE, IO_LOG_FILE)
    syncer = Synchroniser(SOURCE_DIR, REPLICA_DIR, my_logger)
    my_logger.clear_io_logs()
    dir_hash = sync_the_dirs(syncer)
    print("Source hash", dir_hash)

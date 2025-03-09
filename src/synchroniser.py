import os
import hashlib

from dotenv import load_dotenv

from utils.utils import md5_file
from my_logging.logging import *
from syncers.copiers import *

SOURCE_DIR = None
REPLICA_DIR = None
ROOT_DIR = None
IO_LOG_FILE = None

def populate_globals():
    global SOURCE_DIR
    global ROOT_DIR
    global REPLICA_DIR
    global IO_LOG_FILE
    
    load_dotenv('/home/strider/veeam-assignment/.env', override=True)
    ROOT_DIR = os.getenv("ROOT_DIR")
    SOURCE_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("SOURCE_DIR")))
    REPLICA_DIR = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("REPLICA_DIR")))
    # SOURCE_DIR = os.getenv("SOURCE_DIR")
    # REPLICA_DIR = os.getenv("REPLICA_DIR")
    IO_LOG_FILE = os.path.normpath(os.path.join(ROOT_DIR, os.getenv("IO_LOG_FILE")))

def walk_the_dir(dir):
    """
    Merkle tree hash. Only root has stored.
    """
    dir_hashes = {}
    for dirpath, dirnames, filenames in os.walk(dir, topdown=False):
        entries = []
        for filename in sorted(filenames):
            fullpath = os.path.join(dirpath, filename)
            file_hash = md5_file(fullpath)
            sync_file(dirpath, filename, file_hash, SOURCE_DIR, REPLICA_DIR, IO_LOG_FILE)
            entries.append(filename + file_hash)

        for dirname in sorted(dirnames):
            subdir_path = os.path.join(dirpath, dirname)
            sync_dir(dirpath, dirname, SOURCE_DIR, REPLICA_DIR, IO_LOG_FILE)
            if subdir_path in dir_hashes:
                entries.append(dirname + dir_hashes[subdir_path])

        combined = ''.join(entries).encode('utf-8')
        dir_hashes[dirpath] = hashlib.md5(combined).hexdigest()

    return dir_hashes[dir]

if __name__ == '__main__':
    populate_globals()
    dir_hash = walk_the_dir(SOURCE_DIR)
    print("Source hash", dir_hash)

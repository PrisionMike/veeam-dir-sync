import os
import hashlib

from dotenv import load_dotenv

load_dotenv('/home/strider/veeam-assignment/.env')

def test_sync_is_on():
    assert os.getenv("SYNC_ON") == "TRUE"

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def test_replica_copies_source():
    base_dir = os.getenv("ROOT_DIR")
    dir1 = os.path.join(base_dir, os.getenv("SOURCE_DIR"))
    dir2 = os.path.join(base_dir, os.getenv("REPLICA_DIR"))

    files1 = {os.path.relpath(os.path.join(root, f), dir1): hash_file(os.path.join(root, f))
            for root, _, files in os.walk(dir1) for f in files}
    files2 = {os.path.relpath(os.path.join(root, f), dir2): hash_file(os.path.join(root, f))
              for root, _, files in os.walk(dir2) for f in files}
    assert files1 == files2
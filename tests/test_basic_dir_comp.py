import os
import hashlib
import subprocess
import pytest
import shutil

from dotenv import load_dotenv

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


load_dotenv('/home/strider/veeam-assignment/.env', override=True)

BASE_DIR = os.getenv("ROOT_DIR")    
SRC = os.path.join(BASE_DIR, os.getenv("SOURCE_DIR"))
REP = os.path.join(BASE_DIR, os.getenv("REPLICA_DIR"))

def test_sync_is_on():
    assert os.getenv("SYNC_ON") == "TRUE"

@pytest.mark.skip(reason="Does not invoke synchroniser")
def test_replica_copies_source():
    files1 = {os.path.relpath(os.path.join(root, f), SRC): hash_file(os.path.join(root, f))
            for root, _, files in os.walk(SRC) for f in files}
    files2 = {os.path.relpath(os.path.join(root, f), REP): hash_file(os.path.join(root, f))
              for root, _, files in os.walk(REP) for f in files}
    assert files1 == files2

def test_sync_after_invoke():
    result = subprocess.run(
        ["python", "src/synchroniser.py"],  # Command to run the script
        capture_output=True,        # Capture stdout and stderr
        text=True                   # Decode output as text
    )
    files1 = {os.path.relpath(os.path.join(root, f), SRC): hash_file(os.path.join(root, f))
            for root, _, files in os.walk(SRC) for f in files}
    files2 = {os.path.relpath(os.path.join(root, f), REP): hash_file(os.path.join(root, f))
              for root, _, files in os.walk(REP) for f in files}
    assert files1 == files2

def test_clear_replica_then_invoke():
    result = subprocess.run(
        ["rm -r replica2/*"],
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    files1 = {os.path.relpath(os.path.join(root, f), SRC): hash_file(os.path.join(root, f))
            for root, _, files in os.walk(SRC) for f in files}
    files2 = {os.path.relpath(os.path.join(root, f), REP): hash_file(os.path.join(root, f))
              for root, _, files in os.walk(REP) for f in files}
    assert files1 == files2
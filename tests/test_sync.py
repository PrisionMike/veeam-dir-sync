import os
import hashlib
import subprocess
import pytest # type: ignore

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

def compare_dirs(src, rep):
    src_paths = get_all_paths(src)
    rep_paths = get_all_paths(rep)
    assert src_paths == rep_paths

def get_all_paths(dir):
    paths = {}
    for root, dirs, files in os.walk(dir):
        for d in dirs:
            dir_path = os.path.relpath(os.path.join(root, d), dir)
            paths[dir_path] = None

        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), dir)
            paths[file_path] = hash_file(os.path.join(root, f))
    return paths

@pytest.mark.skip(reason="Does not invoke synchroniser")
def test_replica_copies_source():
    compare_dirs(SRC, REP)

def test_sync_invoke_with_current_files():
    result = subprocess.run(
        ["python", "src/synchroniser.py"],  # Command to run the script
        capture_output=True,        # Capture stdout and stderr
        text=True                   # Decode output as text
    )
    compare_dirs(SRC, REP)

# @pytest.mark.skip(reason="Freezing source. Can't delete.")
def test_clear_replica_then_invoke():
    result = subprocess.run(
        ["rm -r replica2/*"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    compare_dirs(SRC, REP)

def test_invoke_replica_surplus():
    result = subprocess.run(
        ["rm -r replica2/* && rm -r source2/*"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["cp -r src-incomp/* source2/ && cp -r src-full/* replica2/"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    compare_dirs(SRC, REP)

def test_invoke_replica_deficit():
    result = subprocess.run(
        ["rm -r replica2/* && rm -r source2/*"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["cp -r src-incomp/* replica2/ && cp -r src-full/* source2/"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    compare_dirs(SRC, REP)

def test_invoke_alpha_beta():
    result = subprocess.run(
        ["rm -r replica2/* && rm -r source2/*"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["cp -r src-alpha/* replica2/ && cp -r src-beta/* source2/"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    compare_dirs(SRC, REP)

def test_invoke_beta_alpha():
    result = subprocess.run(
        ["rm -r replica2/* && rm -r source2/*"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["cp -r src-beta/* replica2/ && cp -r src-alpha/* source2/"], # HARDCODED
        shell=True,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
    compare_dirs(SRC, REP)
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
SRC = os.path.abspath(os.path.join(BASE_DIR, os.getenv("SOURCE_DIR"))) + "/"
REP = os.path.abspath(os.path.join(BASE_DIR, os.getenv("REPLICA_DIR"))) + "/"

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
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def invoke_monoshot_sync():
    result = subprocess.run(
        ["python", "veeam-syncer.py", "monoshot"],
        capture_output=True,
        text=True,
        check=True
    )
    # print(result.stdout)
    # print(result.stderr)
    # assert False

# @pytest.mark.skip(reason="Freezing source. Can't delete.")
def test_clear_replica_then_invoke():
    assert os.path.exists(REP)
    if os.listdir(REP):
        result = subprocess.run(
            ["rm -r " + str(REP)+ "*"],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def test_invoke_replica_surplus():
    clear_src_rep()
    result = subprocess.run(
        ["cp -r test-payloads/src-incomp/* " + str(SRC)+ " && cp -r test-payloads/src-full/* " + str(REP)],
        shell=True,
        capture_output=True,
        text=True,
        check=True
    )
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def clear_src_rep():
    assert os.path.exists(REP)
    assert os.path.exists(SRC)
    if os.listdir(SRC):
        subprocess.run(
            ["rm -r " + str(SRC)+ "*"],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
    if os.listdir(REP):
        subprocess.run(
            ["rm -r " + str(REP)+ "*"],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

def test_invoke_replica_deficit():
    clear_src_rep()
    result = subprocess.run(
        ["cp -r test-payloads/src-incomp/* " + str(REP) + " && cp -r test-payloads/src-full/* " + str(SRC)], # HARDCODED
        shell=True,
        capture_output=True,
        text=True,
        check=True
    )
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def test_invoke_alpha_beta():
    clear_src_rep()
    result = subprocess.run(
        ["cp -r test-payloads/src-alpha/* " + str(REP) + " && cp -r test-payloads/src-beta/* " + str(SRC)], # HARDCODED
        shell=True,
        capture_output=True,
        text=True,
        check=True
    )
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def test_invoke_beta_alpha():
    clear_src_rep()
    result = subprocess.run(
        ["cp -r test-payloads/src-beta/* " + str(REP) + "&& cp -r test-payloads/src-alpha/* " + str(SRC)], # HARDCODED
        shell=True,
        capture_output=True,
        text=True,
        check=True
    )
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)
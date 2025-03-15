import os
import hashlib
import subprocess
import pytest

from random import randint
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
IO_LOG_FILE = os.path.join(BASE_DIR, os.getenv("IO_LOG_FILE"))
SYNC_LOG_FILE = os.path.join(BASE_DIR, os.getenv("SYNC_LOG_FILE"))

def test_sync_is_on():
    assert os.getenv("SYNC_ON") == "TRUE"

def count_files(directory):
    return sum(len(files) for _, _, files in os.walk(directory))

def count_dirs(directory):
    return sum(len(dirs) for _, dirs, _ in os.walk(directory))

def count_log_lines(phrase):
    with open(IO_LOG_FILE, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if phrase in line)

def count_log_lines_in_sync(phrase):
    with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if phrase in line)

@pytest.mark.skip(reason="makedir(S) leads to miscalculations.")
def test_number_of_dirs_created():
    clear_io_and_call()
    src_dir_count = count_dirs(SRC)
    assert count_log_lines('DIR CREATED') == src_dir_count

# @pytest.mark.skip(reason="Freezing source. Can't delete.")
def test_number_of_files_created():
    clear_io_and_call()
    src_file_count = count_files(SRC)
    assert count_log_lines('FILE CREATED') == src_file_count

def test_sync_io_entries():
    num_of_invokations = randint(2,10)
    initial_number_of_entries = count_log_lines_in_sync('SYNCED AT')
    for i in range(num_of_invokations):
        call_syncer()
    assert count_log_lines_in_sync('SYNCED AT') - initial_number_of_entries == num_of_invokations
    

def clear_io_and_call():
    clear_io_log()
    call_syncer()

def clear_io_log():
    open(IO_LOG_FILE, 'w').close() # Clearing log file.
    result = subprocess.run(
        ["rm -r replica2/*"], # HARD CODED
        shell=True,
        capture_output=True,
        text=True
    )

def clear_sync_logs_and_call():
    clear_sync_log()
    call_syncer()

def clear_sync_log():
    open(SYNC_LOG_FILE, 'w').close() # Clearing log file.
    return subprocess.run(
        ["rm -r replica2/*"], # HARD CODED
        shell=True,
        capture_output=True,
        text=True
    )

def call_syncer():
    return subprocess.run(
        ["python", "src/synchroniser.py"],
        capture_output=True,
        text=True
    )
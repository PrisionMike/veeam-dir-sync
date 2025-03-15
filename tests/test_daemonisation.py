import os
import subprocess
import pytest # type: ignore
import time
import psutil # type: ignore

from dotenv import load_dotenv

load_dotenv('/home/strider/veeam-assignment/.env', override=True)

BASE_DIR = os.getenv("ROOT_DIR")    
SRC = os.path.join(BASE_DIR, os.getenv("SOURCE_DIR"))
REP = os.path.join(BASE_DIR, os.getenv("REPLICA_DIR"))
PID_FILE = os.getenv("SYNCER_PID_FILE")

def test_sync_is_on():
    assert os.getenv("SYNC_ON") == "TRUE"

@pytest.fixture
def start_daemon():
    os.chdir(BASE_DIR)
    subprocess.run(["python", "veeam-syncer.py"], check=True)
    time.sleep(2)

def test_main_call_starts_daemon(start_daemon):
    """Checks if the daemon starts"""
    assert os.path.exists(PID_FILE), "PID file was not created."

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    assert psutil.pid_exists(pid), f"Process with PID {pid} is not running."
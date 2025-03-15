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

def get_daemon_pid():
    """Reads the daemon's PID from the PID file."""
    try:
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None
    
def stop_daemon():
    pid = get_daemon_pid()
    if pid:
        os.kill(pid, 15)
        os.remove(PID_FILE)



@pytest.fixture
def start_daemon():
    os.chdir(BASE_DIR)
    stop_daemon()
    subprocess.run(["python", "veeam-syncer.py"], check=True)
    time.sleep(4)
    yield
    stop_daemon()

def test_main_call_starts_daemon(start_daemon):
    """Checks if the daemon starts"""
    assert os.path.exists(PID_FILE), "PID file was not created."

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    assert psutil.pid_exists(pid), f"Process with PID {pid} is not running."

def test_daemon_call_idempotence():
    """Tests multiple invocation of the syncer still lead to only one daemon present."""
    first_pid = get_daemon_pid()
    assert first_pid is not None, "Daemon did not start on first call."

    subprocess.run(["python", "veeam-syncer.py"], check=True)

    second_pid = get_daemon_pid()
    assert second_pid == first_pid, (
        f"Multiple daemons detected: first PID {first_pid} vs second PID {second_pid}"
    )
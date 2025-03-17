import os
import subprocess
import pytest # type: ignore
import time
import psutil # type: ignore

from dotenv import load_dotenv

load_dotenv('./veeam-syncer.env', override=True) # Tests need to be run from root dir.

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
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            print(f"old pid in file.\n {pid} not found. Removing file")
        finally:
            os.remove(PID_FILE)
        # time.sleep(2)

@pytest.fixture
def start_daemon():
    os.chdir(BASE_DIR)
    stop_daemon()
    subprocess.run(["python", "veeam-syncer.py", "start",
                    "--source", "/home/strider/veeam-assignment/test-payloads/source2",
                    "--replica", "/home/strider/veeam-assignment/test-payloads/replica2"],
                    check=True)
    time.sleep(4)
    yield
    stop_daemon()

@pytest.fixture
def start_daemon_dont_stop():
    os.chdir(BASE_DIR)
    stop_daemon()
    subprocess.run(["python", "veeam-syncer.py", "start",
                    "--source", "/home/strider/veeam-assignment/test-payloads/source2",
                    "--replica", "/home/strider/veeam-assignment/test-payloads/replica2"],
                    check=True)    
    time.sleep(2) # Expecting 1 sec sync time. So about 2 rounds in this iteration.

def test_main_call_starts_daemon(start_daemon: None):
    """Checks if the daemon starts"""
    assert os.path.exists(PID_FILE), "PID file was not created."

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    assert psutil.pid_exists(pid), f"Process with PID {pid} is not running."

def test_daemon_call_idempotence(start_daemon: None):
    """Tests multiple invocation of the syncer still lead to only one daemon present."""
    first_pid = get_daemon_pid()
    assert first_pid is not None, "Daemon did not start on first call."

    result = subprocess.run(["python", "veeam-syncer.py", "start",
                    "--source", "/home/strider/veeam-assignment/test-payloads/source2",
                    "--replica", "/home/strider/veeam-assignment/test-payloads/replica2"],
                    check=True,
                    text=True,
                    capture_output=True)

    assert "Daemon already running at:" in result.stdout, "Output warning missing"

    second_pid = get_daemon_pid()
    assert second_pid == first_pid, (
        f"Multiple daemons detected: first PID {first_pid} vs second PID {second_pid}"
    )

def test_daemon_stops(start_daemon_dont_stop: None):
    pid = get_daemon_pid()
    result = subprocess.run(["python", "veeam-syncer.py", "stop"], check=True, capture_output=True, text=True)
    assert "Daemon stopped successfully." in result.stdout
    assert not psutil.pid_exists(pid)
    assert not os.path.exists(PID_FILE)
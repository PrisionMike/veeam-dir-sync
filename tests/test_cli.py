import subprocess
import time
import pytest
import random
import string
import os
import shutil

from dotenv import load_dotenv

from .test_utils import compare_dirs

load_dotenv('./veeam-syncer.env', override=True) # Tests need to be run from root dir.
BASE_DIR = os.getenv("ROOT_DIR")

@pytest.fixture
def prepare_and_compare_dirs():
    os.chdir(BASE_DIR)
    payload_dirs = './test-payloads/'
    src_dir = os.path.abspath(payload_dirs + ''.join(random.choices(string.ascii_letters, k=10)))
    rep_dir = os.path.abspath(payload_dirs + ''.join(random.choices(string.ascii_letters, k=10)))
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(rep_dir, exist_ok=True)

    shutil.copytree(payload_dirs + 'src-alpha/', src_dir, dirs_exist_ok=True)
    shutil.copytree(payload_dirs + 'src-beta/', rep_dir, dirs_exist_ok=True)

    sut_dirs = {
        "src_dir": os.path.abspath(src_dir),
        "rep_dir": os.path.abspath(rep_dir),
    }

    yield sut_dirs
    time.sleep(4)
    compare_dirs(src_dir, rep_dir)

    shutil.rmtree(src_dir)
    shutil.rmtree(rep_dir)


@pytest.fixture(autouse=True)
def stop_the_daemon():
    result = subprocess.run(
        ["python", "veeam-syncer.py", "stop"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "Daemon is not running" in result.stdout \
    or "Daemon stopped successfully." in result.stdout, \
    "Daemon stop is acting weird"

def test_monoshot(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.run(
        ["python", "veeam-syncer.py",
         "monoshot",
         "--source", prepare_and_compare_dirs["src_dir"],
         "--replica", prepare_and_compare_dirs["rep_dir"],
         ],
        capture_output=True,
        text=True,
        check=True
    )
    assert "Starting single shot synchroniser" in result.stdout, result.stderr

@pytest.mark.skip(reason="Test won't stop. Manually test this")
def test_start(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.Popen(
        ["python", "veeam-syncer.py",
         "start",
         "--source", prepare_and_compare_dirs["src_dir"],
         "--replica", prepare_and_compare_dirs["rep_dir"],
         ],
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = result.communicate(timeout=9)
    assert "Daemon started with PID" in stdout, stderr


def test_sync_log_file(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.run(
        ["python", "veeam-syncer.py",
         "monoshot",
         "--source", prepare_and_compare_dirs["src_dir"],
         "--replica", prepare_and_compare_dirs["rep_dir"],
         "--logfile", "test-sync.log"
         ],
        capture_output=True,
        text=True,
        check=True
    )
    assert "Starting single shot synchroniser" in result.stdout, result.stderr

    with open('./test-sync.log', 'r') as f:
        log_content = f.read()
        assert "SYNCED AT" in log_content, "SYNCED AT not found in sync.log"
    
    os.remove('./test-sync.log')

def test_io_log_file(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.run(
        ["python", "veeam-syncer.py",
         "monoshot",
         "--source", prepare_and_compare_dirs["src_dir"],
         "--replica", prepare_and_compare_dirs["rep_dir"],
         "--iologfile", "test-io.log"
         ],
        capture_output=True,
        text=True,
        check=True
    )
    assert "Starting single shot synchroniser" in result.stdout, result.stderr

    with open('./test-io.log', 'r') as f:
        log_content = f.read()
        assert any(event in log_content for event in ["FILE CREATED", "FILE REMOVED", "DIR CREATED", "DIR REMOVED"]), \
            "Expected events not found in io.log"
    
    os.remove('./test-io.log')
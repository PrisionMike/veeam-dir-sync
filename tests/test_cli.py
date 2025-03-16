import subprocess
import pytest
import random
import string
import os
import shutil

from dotenv import load_dotenv

from .test_utils import compare_dirs

load_dotenv('/home/strider/veeam-assignment/.env', override=True)
BASE_DIR = os.getenv("ROOT_DIR")  

@pytest.fixture
def prepare_and_compare_dirs():
    os.chdir(BASE_DIR)
    payload_dirs = './test-payloads/'
    src_dir = payload_dirs + ''.join(random.choices(string.ascii_letters, k=10))
    rep_dir = payload_dirs + ''.join(random.choices(string.ascii_letters, k=10))
    os.makedirs(payload_dirs + src_dir, exist_ok=False)
    os.makedirs(payload_dirs + rep_dir, exist_ok=False)

    shutil.copytree(payload_dirs + 'src-alpha/', src_dir)
    shutil.copytree(payload_dirs + 'src-beta/', rep_dir)

    sut_dirs = {
        "src_dir": os.path.abspath(src_dir),
        "rep_dir": os.path.abspath(rep_dir),
    }

    yield sut_dirs
    assert compare_dirs(src_dir, rep_dir)

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
    assert "Daemon is not running" in result.stdout, "Daemon stop is acting weird"

def test_monoshot(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.run(
        ["python", "veeam-syncer.py",
         "monoshot",
         "--source " + prepare_and_compare_dirs["src_dir"],
         "--replica " + prepare_and_compare_dirs["rep_dir"],
         ],
        capture_output=True,
        text=True,
        check=True
    )
    assert "Starting single shot synchroniser" in result.stdout, "Weird output of single shot sync"


def test_start(prepare_and_compare_dirs: dict[str, str]):
    result = subprocess.run(
        ["python", "veeam-syncer.py",
         "start",
         "--source " + prepare_and_compare_dirs["src_dir"],
         "--replica " + prepare_and_compare_dirs["rep_dir"],
         ],
        capture_output=True,
        text=True,
        check=True
    )

    assert "Daemon started with PID" in result.stdout, "Weird output when starting daemon"

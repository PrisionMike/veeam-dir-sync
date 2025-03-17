import os
import hashlib
import subprocess
import pytest # type: ignore

from dotenv import load_dotenv
from .test_utils import compare_dirs


load_dotenv('./veeam-syncer.env', override=True) # Tests need to be run from root dir.

BASE_DIR = os.getenv("ROOT_DIR")    
SRC = os.path.abspath(os.path.join(BASE_DIR, os.getenv("SOURCE_DIR"))) + "/"
REP = os.path.abspath(os.path.join(BASE_DIR, os.getenv("REPLICA_DIR"))) + "/"

def test_sync_is_on():
    assert os.getenv("SYNC_ON") == "TRUE"

@pytest.mark.skip(reason="Does not invoke synchroniser")
def test_replica_copies_source():
    compare_dirs(SRC, REP)

def test_sync_invoke_with_current_files():
    invoke_monoshot_sync()
    compare_dirs(SRC, REP)

def invoke_monoshot_sync():
   result = subprocess.run(
        ["python", "veeam-syncer.py",
         "monoshot",
         "--source", SRC,
         "--replica", REP,
         ],
        capture_output=True,
        text=True,
        check=True
    )
   assert "Starting single shot synchroniser" in result.stdout, result.stderr

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
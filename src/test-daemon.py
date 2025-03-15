"""Dummy file to test python-daemon. To be deleted."""
import os
import daemon
import time

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SOURCE= os.getenv("SOURCE_DIR")
REPLICA = os.getenv("REPLICA_DIR")
LOG_FILE = os.getenv("SYNC_LOG_FILE")
PWD = os.getenv("ROOT_DIR")

def test_log_write():
    with open(LOG_FILE, 'a') as log_file:
        k = 0
        while k < 5:
            log_file.write(f"--- {datetime.now()} --- TEST ENTRY ---\n")
            log_file.flush()
            time.sleep(2)
            k += 1

if __name__ == '__main__':
    
    with daemon.DaemonContext(working_directory=PWD):
        test_log_write()

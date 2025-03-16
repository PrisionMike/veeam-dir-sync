import os
import argparse
import subprocess
import time

from dotenv import load_dotenv
from psutil import pid_exists, Process # type: ignore

load_dotenv('/home/strider/veeam-assignment/.env', override=True)

# Only used by this program manager file. Not populated by populate_globals()
PID_FILE = os.getenv("SYNCER_PID_FILE")

def get_daemon_pid():
    """Reads the daemon's PID from the PID file."""
    try:
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def is_daemon_running():
    """Checks if the daemon process is running."""
    pid = get_daemon_pid()
    return pid and pid_exists(pid)

def start_daemon():
    """Starts the daemon process."""
    if is_daemon_running():
        print("Daemon already running at:", get_daemon_pid())
        return

    print("Starting sync daemon...")
    subprocess.Popen(["python", "./src/sync_daemon.py"], start_new_session=True)

    if is_daemon_running():
        print(f"Daemon started with PID: {get_daemon_pid()}")
    else:
        print("Failed to start daemon.")

def stop_daemon():
    """Stops the daemon process using the PID file."""
    pid = get_daemon_pid()
    if not pid:
        print("Daemon is not running.")
        return

    print(f"Stopping daemon with PID: {pid}...")
    try:
        daemon = Process(pid)
        daemon.terminate()
        time.sleep(2)           # DON'T REMOVE. WON'T WORK.
        if not is_daemon_running():
            print("Daemon stopped successfully.")
        else:
            print("Daemon did not stop.")
    except ProcessLookupError:
        print("Daemon process not found.")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)  # Ensure PID file is removed

def get_parser():
    parser = argparse.ArgumentParser(description="Veeam demo synchronisation program."
    "Does a continuous one-way synchronisation of the source directory to the replica directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("start", help="'start' to launch the synchroniser. 'stop' to stop previously running daemon")
    subparsers.add_parser("stop", help="'start' to launch the synchroniser. 'stop' to stop previously running daemon")

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.command == "start":
        start_daemon()
    elif args.command == "stop":
        stop_daemon()

if __name__ == "__main__":
    main()
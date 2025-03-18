import os
import argparse
import subprocess
import time

from dotenv import load_dotenv
from psutil import pid_exists, Process, NoSuchProcess # type: ignore

load_dotenv('/home/strider/veeam-assignment/.env', override=True)

PID_FILE = "/tmp/veeam-syncer.pid"
ENV_FILE = os.path.abspath("./veeam-syncer.env")

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
    time.sleep(1) # DON'T REMOVE OR THE FOLLOWING IF WOULD FAIL. Functionality unaffected
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
    except (ProcessLookupError, NoSuchProcess):
        print("Daemon process not found.")
        print("Daemon is not running.")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)  # Ensure PID file is removed

def run_once():
    pid = get_daemon_pid()
    if pid:
        stop_daemon()
    print("Starting single shot synchroniser...")
    subprocess.Popen(["python", "./src/sync_daemon.py", "monoshot"], start_new_session=True)

def add_common_arguments(subparser):
    subparser.add_argument("--source", "-s", required=True, help="Path to the source directory")
    subparser.add_argument("--replica", "-r", required=True, help="Path to the destination (replica) directory")
    subparser.add_argument("--logfile", "-l", default="synchronisation.log", help="Path to the main syncer log file")
    subparser.add_argument("--iologfile", "-i", default="file-io.log", help="Path to the IO log file")

def get_parser():
    parser = argparse.ArgumentParser(description="Veeam demo synchronisation program."
    "Does a continuous one-way synchronisation of the source directory to the replica directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    start_subparser = subparsers.add_parser("start", help="Starts the synchroniser")
    add_common_arguments(start_subparser)

    subparsers.add_parser("stop", help="Stops any pre-running synchroniser")
    
    monoshot_subparser = subparsers.add_parser("monoshot", help="Runs the syncer once then stop. Stops any pre-existing daemons.")
    add_common_arguments(monoshot_subparser)

    return parser

def write_env_file(env_dict):
    """Writes the environment variables to veeam-syncer.env"""
    env_lines = [f"{key}={value}" for key, value in env_dict.items()]
    content = "\n".join(sorted(env_lines))  # Sorting for consistency

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content + "\n")  # Ensure newline at end

def read_env_file():
    """Reads the existing .env file and returns a dictionary of environment variables."""
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    env_vars[key.strip()] = value.strip()
    return env_vars

def prepare_env_variables(args):
    """Prepares and writes environment variables to veeam-syncer.env"""
    env_vars = read_env_file() 
    env_vars["ROOT_DIR"] = os.getcwd()
    env_vars["PID_FILE"] = PID_FILE
    
    if hasattr(args, "source"):
        env_vars["SOURCE_DIR"] = args.source

    if hasattr(args, "replica"):
        env_vars["REPLICA_DIR"] = args.replica

    if hasattr(args, "logfile"):
        env_vars["SYNC_LOG_FILE"] = args.logfile

    if hasattr(args, "iologfile"):
        env_vars["IO_LOG_FILE"] = args.iologfile

    write_env_file(env_vars)

def main():
    parser = get_parser()
    args = parser.parse_args()
    prepare_env_variables(args)

    if args.command == "start":
        start_daemon()
    elif args.command == "stop":
        stop_daemon()
    elif args.command == "monoshot":
        run_once()

if __name__ == "__main__":
    main()
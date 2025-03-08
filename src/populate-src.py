import os
import random
import string
import time
import shutil

from dotenv import load_dotenv
from datetime import datetime

INTERVAL = 3

load_dotenv('../.env')

BASE_DIR = os.getenv("SOURCE_DIR")

def random_string(length=10):
    """Generate a random string of given length."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_random_structure(base_dir, depth=2, max_files=4):
    """
    Creates a nested directory structure (of given depth) under base_dir and
    adds a few random files with random text.
    """
    current_dir = base_dir
    # Create nested directories
    for _ in range(depth):
        dir_name = "dir_" + random_string(5)
        current_dir = os.path.join(current_dir, dir_name)
        os.makedirs(current_dir, exist_ok=True)
    
    # Create a random number (1 to max_files) of files in the deepest folder
    num_files = random.randint(1, max_files)
    for _ in range(num_files):
        file_name = "file_" + random_string(5) + ".txt"
        file_path = os.path.join(current_dir, file_name)
        # Write a small random text snippet into the file
        with open(file_path, "w") as f:
            f.write(random_string(50))
    
    print(f"[{datetime.now()}] Created structure in: {current_dir}")

def create_random_file_in_root(base_dir):
    """Create a random file directly in the base directory."""
    file_name = "file_" + random_string(5) + ".txt"
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, "w") as f:
        f.write(random_string(50))
    print(f"[{datetime.now()}] Created file in base: {file_path}")

def delete_random_elements(base_dir, deletion_probability=0.2):
    """
    Delete some random files and folders within base_dir.
    """
    all_files = []
    all_dirs = []

    for root, dirs, files in os.walk(base_dir):
        for f in files:
            all_files.append(os.path.join(root, f))
        for d in dirs:
            all_dirs.append(os.path.join(root, d))

    for f in all_files:
        if random.random() < deletion_probability:
            try:
                os.remove(f)
                print(f"[{datetime.now()}] Deleted file: {f}")
            except Exception as e:
                print(f"[{datetime.now()}] Error deleting file {f}: {e}")
    
    # Sort directories so that deeper directories come first
    all_dirs.sort(key=lambda x: x.count(os.sep), reverse=True)
    for d in all_dirs:
        if random.random() < deletion_probability:
            try:
                os.rmdir(d)  # Only works if directory is empty
                print(f"[{datetime.now()}] Deleted directory: {d}")
            except Exception:
                # If not empty, delete recursively
                try:
                    shutil.rmtree(d)
                    print(f"[{datetime.now()}] Recursively deleted directory: {d}")
                except Exception as e:
                    print(f"[{datetime.now()}] Error deleting directory {d}: {e}")

def show_progress(interval):
    """
    Display a continuous progress indicator message for the given interval.
    """
    message = "Source driving being used by simulation"
    print(message, end='', flush=True)
    for i in range(interval):
        print('.', end='', flush=True)
        time.sleep(1)
    print()  # Move to the next line

if __name__ == "__main__":
    # Ensure the base simulation directory exists
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # Run the simulation indefinitely
    while True:
        if random.random() < 0.6:
            create_random_structure(BASE_DIR)
        else:
            create_random_file_in_root(BASE_DIR)
        
        delete_random_elements(BASE_DIR, deletion_probability=0.1)

        show_progress(INTERVAL)

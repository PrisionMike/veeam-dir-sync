import os
import random
import string
import time

from dotenv import load_dotenv
from datetime import datetime

INTERVAL = 3

load_dotenv('../.env')

BASE_DIR = os.getenv("SOURCE_DIR")

def random_string(length=10):
    """Generate a random string of given length."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_random_structure(base_dir, depth=2, max_files=3):
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
        create_random_structure(BASE_DIR)
        show_progress(INTERVAL)

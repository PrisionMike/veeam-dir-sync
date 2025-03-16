import hashlib
import os

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def compare_dirs(src: str, rep: str) -> bool:
    src_paths = get_all_paths(src)
    rep_paths = get_all_paths(rep)
    assert src_paths == rep_paths

def get_all_paths(dir):
    paths = {}
    for root, dirs, files in os.walk(dir):
        for d in dirs:
            dir_path = os.path.relpath(os.path.join(root, d), dir)
            paths[dir_path] = None

        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), dir)
            paths[file_path] = hash_file(os.path.join(root, f))
    return paths
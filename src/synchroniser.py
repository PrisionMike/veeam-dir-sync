import os
import hashlib

def md5_file(filepath):
    """Compute the MD5 hash of a file by reading it in chunks."""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()

def compute_directory_hash(root):
    """
    Compute a full directory hash (Merkle tree style) using a DFS approach.
    This function uses os.walk with topdown=False (i.e. bottom-up)
    so that subdirectories are processed before their parents.
    """
    dir_hashes = {}
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        entries = []
        # Process files: get each file's hash and combine with its name.
        for filename in sorted(filenames):
            fullpath = os.path.join(dirpath, filename)
            file_hash = md5_file(fullpath)
            entries.append(filename + file_hash)
        # Process subdirectories: use precomputed hash for each.
        for dirname in sorted(dirnames):
            subdir_path = os.path.join(dirpath, dirname)
            if subdir_path in dir_hashes:
                entries.append(dirname + dir_hashes[subdir_path])
        # Combine all entry strings, encode as bytes, and compute MD5.
        combined = ''.join(entries).encode('utf-8')
        dir_hashes[dirpath] = hashlib.md5(combined).hexdigest()
    # Return the hash for the root directory.
    return dir_hashes[root]

if __name__ == '__main__':
    root_directory = "your_directory_path"  # Replace with your directory path.
    full_hash = compute_directory_hash(root_directory)
    print("Full directory hash:", full_hash)

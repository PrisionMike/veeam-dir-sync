import hashlib

def md5_file(filepath):
    """Compute the MD5 hash of a file by reading it in chunks."""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()
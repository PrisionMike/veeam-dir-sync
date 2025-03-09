import shutil
from os import (path,
                makedirs,
                listdir,
                remove)

from utils.utils import md5_file
from my_logging.logging import *

def sync_file(dirpath, filename, file_hash, source_path, replica_path, log_file):
    rel_path = path.relpath(dirpath, source_path)
    replica_dir = path.join(replica_path, rel_path)
    if not path.exists(replica_dir):
        makedirs(replica_dir, exist_ok=True)
        log_dir_created(replica_dir, log_file)
    source_file_path = path.join(dirpath, filename)
    replica_file_path = path.join(replica_dir, filename)
    if not path.exists(replica_file_path):
        shutil.copyfile(source_file_path, replica_file_path)
        log_file_created(replica_file_path, file_hash, log_file)
    else:
        replica_file_hash = md5_file(replica_file_path)
        if replica_file_hash != file_hash:
            shutil.copyfile(source_file_path, replica_file_path)
            log_file_updated(replica_file_path, file_hash, log_file)
    
def sync_dir(dirpath, dirname, src_dir, replica_path, log_file):
    rel_path = path.relpath(dirpath, src_dir)
    replica_dir = path.join(replica_path, rel_path)
    replica_subdir = path.join(replica_dir, dirname)
    if not path.exists(replica_subdir):
        makedirs(replica_subdir, exist_ok=True)
        log_dir_created(replica_subdir, log_file)

def sync_prune(dirpath, dirnames, filenames, source_path, replica_path, log_file):
    rel_path = path.relpath(dirpath, source_path)
    replica_dir = path.join(replica_path, rel_path)
    rep_members = listdir(replica_dir)
    
    [remove_dir(x, dirpath, log_file)
     for x in rep_members
     if x not in dirnames and path.isdir(x)]
    
    [remove_file(x, dirpath, log_file)
     for x in rep_members
     if x not in filenames and path.isfile(x)]

def remove_dir(dir, dirpath, log_file):
    full_path = path.join(dirpath, dir)
    log_dir_removed(full_path, log_file)
    shutil.rmtree(full_path)

def remove_file(file, dirpath, log_file):
    full_path = path.join(dirpath, file)
    log_file_removed(full_path, log_file)
    remove(full_path)
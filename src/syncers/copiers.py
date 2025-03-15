import shutil
from os import (path,
                makedirs,
                listdir,
                remove)

from utils.utils import md5_file
from my_logging.logging import MyLogger

class Synchroniser:
    def __init__(self, source_path, replica_path, my_logger: MyLogger):
        self.source_path = source_path
        self.replica_path = replica_path
        self.my_logger = my_logger

    def sync_file(self, dirpath, filename, file_hash):
        rel_path = path.relpath(dirpath, self.source_path)
        replica_dir = path.join(self.replica_path, rel_path)
        if not path.exists(replica_dir):
            makedirs(replica_dir, exist_ok=True)
            self.my_logger.log_dir_created(replica_dir)
        source_file_path = path.join(dirpath, filename)
        replica_file_path = path.join(replica_dir, filename)
        if not path.exists(replica_file_path):
            shutil.copyfile(source_file_path, replica_file_path)
            self.my_logger.log_file_created(replica_file_path, file_hash)
        else:
            replica_file_hash = md5_file(replica_file_path)
            if replica_file_hash != file_hash:
                shutil.copyfile(source_file_path, replica_file_path)
                self.my_logger.log_file_updated(replica_file_path, file_hash)
    
    def sync_dir(self, dirpath, dirname):
        rel_path = path.relpath(dirpath, self.source_path)
        replica_dir = path.join(self.replica_path, rel_path)
        replica_subdir = path.join(replica_dir, dirname)
        if not path.exists(replica_subdir):
            makedirs(replica_subdir, exist_ok=True)
            self.my_logger.log_dir_created(replica_subdir)

    def sync_prune(self, dirpath, dirnames, filenames):
        rel_path = path.relpath(dirpath, self.source_path)
        replica_dirpath = path.join(self.replica_path, rel_path)
        try:
            rep_members = listdir(replica_dirpath)

            for mem in rep_members:
                mem_path = path.join(replica_dirpath, mem)
                if mem not in dirnames and path.isdir(mem_path):
                    self.remove_dir(mem_path)
                if mem not in filenames and path.isfile(mem_path):
                    self.remove_file(mem_path)
        except FileNotFoundError:
            pass

    def remove_dir(self, mem_path):
        self.my_logger.log_dir_removed(mem_path)
        shutil.rmtree(mem_path)

    def remove_file(self, mem_path):
        self.my_logger.log_file_removed(mem_path)
        remove(mem_path)
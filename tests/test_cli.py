import subprocess
import pytest
import random
import string
import os

@pytest.fixture
def prepare_src_rep_dirs():
    src_dir_name = random.choices(string.ascii_letters, 10)
    rep_dir_name = random.choices(string.ascii_letters, 10)
    
import pytest
from mgnipy._internal_functions import create_folder

def test_create_folder():
    # setup
    folder_name = "THIS_IS_A_TEST_TEMP_FOLDER"
    import os
    # test
    create_folder(folder_name)
    assert os.path.isdir(folder_name)
    # teardown
    os.rmdir(folder_name)
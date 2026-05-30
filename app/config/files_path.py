import os

SHARED_FILES_PATH = "files/shared"

UNSHARED_FILES_PATH = "files/unshared"

def create_folders():
    os.makedirs(f"{SHARED_FILES_PATH}", exist_ok=True)

    os.makedirs(f"{UNSHARED_FILES_PATH}", exist_ok=True)



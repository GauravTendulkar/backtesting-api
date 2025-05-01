import json
from filelock import FileLock

# file_path = "data.json"
# lock_path = file_path + ".lock"

def lock_file(file_path):
    
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path)
    return lock

def save_data_thread_safe(data, file_path):
    # lock_path = file_path + ".lock"
    """Safely writes data to a JSON file using a file lock."""
    # with FileLock(lock_path):  # Lock the file
    with open(file_path, "w") as file:
        json.dump(data, file)

def load_data_thread_safe(file_path):
    # lock_path = file_path + ".lock"
    """Safely reads data from a JSON file using a file lock."""
    # with FileLock(lock_path):  # Lock the file
    with open(file_path, "r") as file:
        return json.load(file)
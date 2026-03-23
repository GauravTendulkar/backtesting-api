import os
def get_folder_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_folder_size(entry.path)
    return total

def sizeof_fmt(num, suffix='B', unit="Gi"):
    for i in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if i == unit:
            # return f"{num:3.1f}{unit}{suffix}"
            return [num, f"{unit}{suffix}"]
        num /= 1024.0
    # return f"{num:.1f}Yi{suffix}"
    return [num, f"Yi{suffix}"]

# sizeof_fmt(get_folder_size("fastCache"), unit="Gi")
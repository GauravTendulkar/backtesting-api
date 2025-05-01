from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

cache_for_nparray = ThreadSafeLRUCache(maxsize=128)

cache_ts = ThreadSafeLRUCache(maxsize=128000)


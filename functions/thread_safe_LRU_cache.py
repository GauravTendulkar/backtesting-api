from collections import OrderedDict
from threading import Lock

class ThreadSafeLRUCache:
    def __init__(self, maxsize=128):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.lock = Lock()

    def _make_key(self, *args, **kwargs):
        """
        Create a hashable key from function arguments.
        Combines positional and keyword arguments into a tuple.
        """
        return (args, tuple(sorted(kwargs.items())))

    def get(self, *args, **kwargs):
        """
        Retrieve the cached value using the arguments as the key.
        """
        key = self._make_key(*args, **kwargs)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return "Not Found"

    def set(self, value, *args, **kwargs):
        """
        Store the value in the cache using the arguments as the key.
        """
        key = self._make_key(*args, **kwargs)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.maxsize:
                    self.cache.popitem(last=False)
            self.cache[key] = value
        # print("self.cache", self.cache)
    def return_all_cache(self):
        with self.lock:
            return OrderedDict(self.cache)
    
    def update_cache(self, o_dict):
        with self.lock:
            self.cache.update(o_dict)

    def get_cache_size(self):
        with self.lock:
            return len(self.cache)

    def __repr__(self):
        """String representation of the cache for debugging."""
        with self.lock:
            return f"ThreadSafeLRUCache({list(self.cache.items())})"
            

# from collections import OrderedDict
# from threading import Lock

# class ThreadSafeLRUCache:
#     def __init__(self, maxsize=128):
#         self.cache = OrderedDict()
#         self.maxsize = maxsize
#         # self.lock = Lock()

#     def _make_key(self, *args, **kwargs):
#         """
#         Create a hashable key from function arguments.
#         Combines positional and keyword arguments into a tuple.
#         """
#         return (args, tuple(sorted(kwargs.items())))

#     def get(self, *args, **kwargs):
#         """
#         Retrieve the cached value using the arguments as the key.
#         """
#         key = self._make_key(*args, **kwargs)
        
#         if key in self.cache:
#             self.cache.move_to_end(key)
#             return self.cache[key]
#         return "Not Found"

#     def set(self, value, *args, **kwargs):
#         """
#         Store the value in the cache using the arguments as the key.
#         """
#         key = self._make_key(*args, **kwargs)
        
#         if key in self.cache:
#             self.cache.move_to_end(key)
#         else:
#             if len(self.cache) >= self.maxsize:
#                 self.cache.popitem(last=False)
#             self.cache[key] = value
#         # print("self.cache", self.cache)
#     def return_all_cache(self):
        
#         return OrderedDict(self.cache)
    
#     def update_cache(self, o_dict):
        
#             self.cache.update(o_dict)

#     def __repr__(self):
#         """String representation of the cache for debugging."""
        
#         return f"ThreadSafeLRUCache({list(self.cache.items())})"

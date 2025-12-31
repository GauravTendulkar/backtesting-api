

class DictCache:
    def __init__(self, max_size=None):
        self.cache = {}
        self.max_size = max_size

    def set(self, key, value):
        if self.max_size and len(self.cache) >= self.max_size:
            # Optional: remove an arbitrary item, or implement eviction strategies
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()

    def __contains__(self, key):
        return key in self.cache

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cache})"
    

# create cache instance
myCache = DictCache()
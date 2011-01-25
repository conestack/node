# STUB

class Cache(object):
    def __getitem__(_next, self, key):
        # - check if key is in cache
        # - check if cached item is still valid
        # - return if valid
        # - remove from cache
        # - fetch new item from _next
        # - put item in cache
        # - return item
        pass
    
    def invalidate(self, key=None):
        pass


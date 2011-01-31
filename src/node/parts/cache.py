from plumber import (
    Part,
    default,
    plumb,
)
from node.interfaces import (
    IInvalidate,
    ICache,
)
from zope.interface import implements


# XXX: This looks like it deletes all children in the storage, not in the cache
class Invalidate(Part):
    implements(IInvalidate)
    
    @default
    def invalidate(self, key=None):
        """Invalidate Child with key or all children.
        
        Raise KeyError if child does not exist for key if given.
        """
        if key is not None:
            del self[key]
        else:
            # need to use keys instead of iter here
            for key in self.keys():
                del self[key]


class Cache(Part):
    implements(ICache)
    
    @default
    @property
    def cache(self):
        """Default cache is a dict on self.
        """
        if not hasattr(self, '_cache'):
            self._cache = dict()
        return self._cache
    
    @plumb
    def invalidate(_next, self, key=None):
        cache = self.cache
        if key is not None:
            try:
                del cache[key]
            except KeyError:
                pass
        else:
            for key in cache.keys():
                try:
                    del cache[key]
                except KeyError:
                    pass
        _next(self, key=key)
    
    @plumb
    def __getitem__(_next, self, key):
        cache = self.cache
        try:
            return cache[key]
        except KeyError:
            cache[key] = _next(self, key)
        return cache[key]

    # XXX: think of using subscribers instead of plumbings for cache
    #      invalidation on __setitem__, __delitem__, __iter__.
    #      but this makes us depend caching to lifecycle.
    
    @plumb
    def __setitem__(_next, self, key, value):
        try:
            del self.cache[key]
        except KeyError:
            pass
        _next(self, key, value)
    
    @plumb
    def __delitem__(_next, self, key):
        try:
            del self.cache[key]
        except KeyError:
            pass
        _next(self, key)
    
    @plumb
    def __iter__(_next, self):
        # XXX
        return _next(self)
    

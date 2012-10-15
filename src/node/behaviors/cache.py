from plumber import (
    Behavior,
    default,
    plumb,
)
from zope.interface import implementer
from ..interfaces import (
    IInvalidate,
    ICache,
)
from ..utils import instance_property


@implementer(IInvalidate)
class Invalidate(Behavior):
    """Plumbing behavior for invalidation.

    This basic implementation assumes that nodes using this behavior are NOT
    storage related. It just uses ``self.__delitem__``.
    """

    @default
    def invalidate(self, key=None):
        """Raise KeyError if child does not exist for key if given.
        """
        if key is not None:
            del self[key]
        else:
            # need to use keys instead of iter here
            for key in self.keys():
                del self[key]


@implementer(ICache)
class Cache(Behavior):

    @default
    @instance_property
    def cache(self):
        """Default cache is a dict on self.
        """
        return dict()

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
                del cache[key]
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
    #
    #      might be another caching mechanism, both caching variants are
    #      possible then.

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
        # do not cache keys on default implementation.
        return _next(self)

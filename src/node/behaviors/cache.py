# -*- coding: utf-8 -*-
from node.compat import IS_PY2
from node.interfaces import ICache
from node.interfaces import IInvalidate
from node.utils import instance_property
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer


def _keys(obj):
    """Compat function to always get keys as list.

    Currently used to avoid modification of dict while iterating in python 3.
        for key in _keys(ob):
            del ob[key]

    Can probably be replaced by just using.
        ob.clear()

    Business logic changes after whole stack has been migrated to python 3.
    """
    return obj.keys() if IS_PY2 else list(obj.keys())


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
            for key in _keys(self):
                del self[key]


@implementer(IInvalidate)
class VolatileStorageInvalidate(Behavior):
    """Plumbing behavior for invalidating volatile storages like
    ``DictStorage`` or ``OdictStorage``.
    """

    @default
    def invalidate(self, key=None):
        """Raise KeyError if child does not exist for key if given.
        """
        storage = self.storage
        if key is not None:
            if key in _keys(self):
                try:
                    del storage[key]
                except KeyError:
                    pass  # ignore, key is valid, but not on storage right now
            else:
                raise KeyError(key)
        else:
            for key in _keys(storage):
                del storage[key]


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
            for key in _keys(cache):
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

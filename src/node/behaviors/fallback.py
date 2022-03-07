from __future__ import absolute_import
from node.interfaces import IFallback
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer
import threading


_marker = dict()


class fallback_processing(object):
    data = threading.local()
    data.processing = -1

    def __enter__(self):
        self.data.processing += 1
        return self.data.processing

    def __exit__(self, type, value, traceback):
        self.data.processing -= 1


def _to_root(node, path, visited):
    """Traverse to root searching next fallback key. If no more parent, break.
    """
    parent = node.__parent__
    if parent is None:
        return _marker
    if not getattr(parent, 'fallback_key', _marker) or node in visited:
        return _to_root(parent, path=path, visited=visited)
    visited.update({node})
    return _to_leaf(parent[parent.fallback_key], path=path, visited=visited)


def _to_leaf(node, path, visited):
    """Traverse children, searching for fallback key."""
    current = node
    for name in path[len(current.path):]:
        new_current = current.get(name, _marker)
        if new_current is _marker:
            return _to_root(current, path=path, visited=visited)
        current = new_current
    return current


@implementer(IFallback)
class Fallback(Behavior):
    fallback_key = default(_marker)

    @plumb
    def __getitem__(next_, self, key):
        """If key not found, look for fallback_key on parent(s) with the same
        subpath, take it's children and look there, fall back to unvisited
        parents until no fallback left.
        """
        try:
            value = next_(self, key)
        except KeyError:
            with fallback_processing() as count:
                if count > 0:
                    raise
                value = _to_root(self, path=self.path + [key], visited=set())
                if value is _marker:
                    raise
        return value

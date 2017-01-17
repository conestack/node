# -*- coding: utf-8 -*-
from node.interfaces import IFallback
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer

import threading

thread_data = threading.local()
thread_data.in_fallback_processing = False

_marker = dict()


def _to_root(node, path, visited):
    """go in direction root until node with fallback found.
    or no more parent (breaks)
    """
    parent = node.__parent__
    if parent is None:
        return _marker
    if not getattr(parent, 'fallback_key', _marker) or node in visited:
        return _to_root(parent, path=path, visited=visited)
    visited.update({node})
    return _to_leaf(parent[parent.fallback_key], path=path, visited=visited)


def _to_leaf(node, path, visited):
    """go to the leaf, is the key?"""
    current = node
    for name in path[len(current.path):]:
        new_current = current.get(name, _marker)
        if new_current is _marker:
            return _to_root(current, path=path, visited=visited)
        current = new_current
    return current


@implementer(IFallback)
class Fallback(Behavior):
    """looks for a fallback_key in parent
    (or in its parents in the same children path),
    takes its children and looks there,
    falls back to unvisited parents,
    untils no fallback left
    """

    fallback_key = default(_marker)

    @plumb
    def __getitem__(_next, self, key):
        try:
            value = _next(self, key)
        except KeyError:
            if thread_data.in_fallback_processing:
                raise
            try:
                thread_data.in_fallback_processing = True
                value = _to_root(self, path=self.path + [key], visited=set())
            finally:
                thread_data.in_fallback_processing = False
            if value is _marker:
                raise
        return value

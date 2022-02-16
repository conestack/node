from __future__ import absolute_import
from contextlib import contextmanager
from node.interfaces import IMappingAdopt
from node.interfaces import INode
from node.interfaces import ISequenceAdopt
from plumber import Behavior
from plumber import plumb
from zope.interface import implementer


@contextmanager
def adopt_node(name, parent, value):
    """Context manager for setting name and parent on node. If exception
    occurs, name and parent gets reverted to original values.
    """
    # Only care about adoption if we have a node.
    if not INode.providedBy(value):
        yield
        return
    # Save old __parent__ and __name__ to restore if something goes wrong.
    old_name = value.__name__
    old_parent = value.__parent__
    value.__name__ = name
    value.__parent__ = parent
    try:
        yield
    except Exception:
        value.__name__ = old_name
        value.__parent__ = old_parent
        raise


@implementer(IMappingAdopt)
class MappingAdopt(Behavior):

    @plumb
    def __setitem__(next_, self, key, value):
        with adopt_node(key, self, value):
            next_(self, key, value)

    @plumb
    def setdefault(next_, self, key, default=None):
        # Reroute through ``__getitem__`` and ``__setitem__``, skipping
        # ``next_``.
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default


@implementer(ISequenceAdopt)
class SequenceAdopt(Behavior):

    @plumb
    def __setitem__(next_, self, index, value):
        if type(index) is slice:
            raise NotImplementedError('No slice support.')
        with adopt_node(str(index), self, value):
            next_(self, index, value)

    @plumb
    def insert(next_, self, index, value):
        with adopt_node(str(index), self, value):
            next_(self, index, value)

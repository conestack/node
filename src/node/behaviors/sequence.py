from __future__ import absolute_import
try:  # pragma: no cover
    from collections.abc import MutableSequence as ABCMutableSequence
    from collections.abc import Sequence as ABCSequence
except ImportError:  # pragma: no cover
    from collections import MutableSequence as ABCMutableSequence
    from collections import Sequence as ABCSequence
from node.behaviors.node import ContentishNode
from node.compat import IS_PY2
from node.interfaces import INode
from node.interfaces import ISequenceNode
from plumber import Behavior
from plumber import default
from plumber import override
from plumber import plumb
from zope.interface import implementer
from zope.interface.common.collections import IMutableSequence
from zope.interface.common.collections import ISequence
import functools
import types


def copy_func(f):
    """Copy function.

    Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)
    """
    fn = types.FunctionType(
        f.func_code if IS_PY2 else f.__code__,
        f.func_globals if IS_PY2 else f.__globals__,
        name=f.func_name if IS_PY2 else f.__name__,
        argdefs=f.func_defaults if IS_PY2 else f.__defaults__,
        closure=f.func_closure if IS_PY2 else f.__closure__
    )
    fn = functools.update_wrapper(fn, f)
    if not IS_PY2:  # pragma: no cover
        fn.__kwdefaults__ = f.__kwdefaults__
    return fn


@implementer(ISequence)
class Sequence(Behavior):
    __contains__ = default(copy_func(ABCSequence.__contains__))
    __iter__ = default(copy_func(ABCSequence.__iter__))
    __reversed__ = default(copy_func(ABCSequence.__reversed__))
    count = default(copy_func(ABCSequence.count))
    index = default(copy_func(ABCSequence.index))

    @default
    def __len__(self):
        raise NotImplementedError

    @default
    def __getitem__(self, index):
        raise NotImplementedError


@implementer(IMutableSequence)
class MutableSequence(Sequence):
    __iadd__ = default(copy_func(ABCMutableSequence.__iadd__))
    append = default(copy_func(ABCMutableSequence.append))
    # Missing in python 2
    # clear = default(copy_func(ABCMutableSequence.clear))
    extend = default(copy_func(ABCMutableSequence.extend))
    pop = default(copy_func(ABCMutableSequence.pop))
    remove = default(copy_func(ABCMutableSequence.remove))
    reverse = default(copy_func(ABCMutableSequence.reverse))

    @default
    def __setitem__(self, index, value):
        raise NotImplementedError

    @default
    def __delitem__(self, index):
        raise NotImplementedError

    @default
    def insert(self, index, value):
        raise NotImplementedError

    @default
    def clear(self):
        # Missing in python 2
        try:
            while True:
                self.pop()
        except IndexError:
            pass


@implementer(ISequenceNode)
class SequenceNode(ContentishNode, MutableSequence):

    @override
    def __index__(self):
        try:
            return int(self.__name__)
        except (TypeError, ValueError):
            raise IndexError('Node not member of a sequence node')

    @plumb
    def __getitem__(next_, self, index):
        if type(index) is not slice:
            index = int(index)
        return next_(self, index)

    @plumb
    def __setitem__(next_, self, index, value):
        if type(index) is not slice:
            index = int(index)
        next_(self, index, value)

    @plumb
    def __delitem__(next_, self, index):
        if type(index) is not slice:
            index = int(index)
        next_(self, index)
        self._update_indices()

    @plumb
    def insert(next_, self, index, value):
        next_(self, int(index), value)
        self._update_indices()

    @plumb
    def detach(next_, self, index):
        node = next_(self, int(index))
        self._update_indices()
        return node

    @default
    def _update_indices(self):
        for index, value in enumerate(self):
            if INode.providedBy(value):
                value.__name__ = str(index)

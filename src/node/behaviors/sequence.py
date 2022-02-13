# -*- coding: utf-8 -*-
try:
    from collections.abc import MutableSequence as ABCMutableSequence
    from collections.abc import Sequence as ABCSequence
except ImportError:
    from _abccoll import MutableSequence as ABCMutableSequence
    from _abccoll import Sequence as ABCSequence
from node.utils import instance_property
from plumber import Behavior
from plumber import default


"""
Sized:
    __len__ (abstract)
Iterable:
    __iter__ (abstract)
Container:
    __contains__ (abstract)
Collection(Sized, Iterable, Container)
Reversible:
    __reversed__ (abstract)
Sequence(Reversible, Collection)
    __getitem__ (abstract)
    __len__ (abstract, from Sized)
    __iter__ (Iterable implementation)
    __contains__ (Container implementation)
    __reversed__ (Reversible impementation)
    index
    count
MutableSequence(Sequence)
    __setitem__ (abstract)
    __delitem__ (abstract)
    insert (abstract)
    append
    clear
    reverse
    extend
    pop
    remove
    __iadd__
"""


class Sequence(Behavior):
    __iter__ = default(ABCSequence.__iter__)
    __contains__ = default(ABCSequence.__contains__)
    __reversed__ = default(ABCSequence.__reversed__)
    index = default(ABCSequence.index)
    count = default(ABCSequence.count)

    @default
    def __getitem__(self, idx):
        raise NotImplementedError

    @default
    def __len__(self):
        raise NotImplementedError


class MutableSequence(Sequence):
    append = default(ABCMutableSequence.append)
    clear = default(ABCMutableSequence.clear)
    reverse = default(ABCMutableSequence.reverse)
    extend = default(ABCMutableSequence.extend)
    pop = default(ABCMutableSequence.pop)
    remove = default(ABCMutableSequence.remove)
    __iadd__ = default(ABCMutableSequence.__iadd__)

    @default
    def __setitem__(self, idx, val):
        raise NotImplementedError

    @default
    def __delitem__(self, idx):
        raise NotImplementedError

    @default
    def insert(self, idx, val):
        raise NotImplementedError


class ListStorage(Behavior):

    @default
    @instance_property
    def storage(self):
        return list()

    @default
    def __getitem__(self, idx):
        return self.storage[idx]

    @default
    def __setitem__(self, idx, val):
        self.storage[idx] = val

    @default
    def __delitem__(self, idx):
        del self.storage[idx]

    @default
    def insert(self, idx, val):
        self.storage.insert(idx, val)

    @default
    def __len__(self):
        return len(self.storage)

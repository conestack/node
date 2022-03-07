from __future__ import absolute_import
from node.interfaces import IMappingStorage
from node.interfaces import IOrdered
from node.interfaces import ISequenceStorage
from node.utils import instance_property
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import override
from zope.interface import implementer


@implementer(IMappingStorage)
class MappingStorage(Behavior):

    @default
    @property
    def storage(self):
        msg = 'Abstract ``MappingStorage`` does not implement ``storage``'
        raise NotImplementedError(msg)

    @override
    def __getitem__(self, key):
        return self.storage[key]

    @override
    def __delitem__(self, key):
        del self.storage[key]

    @override
    def __setitem__(self, key, val):
        self.storage[key] = val

    @override
    def __iter__(self):
        return self.storage.__iter__()


class DictStorage(MappingStorage):

    @default
    @instance_property
    def storage(self):
        return dict()


@implementer(IOrdered)
class OdictStorage(MappingStorage):

    @default
    @instance_property
    def storage(self):
        return odict()


@implementer(ISequenceStorage)
class SequenceStorage(Behavior):

    @default
    @property
    def storage(self):
        msg = 'Abstract ``SequenceStorage`` does not implement ``storage``'
        raise NotImplementedError(msg)

    @override
    def __len__(self):
        return len(self.storage)

    @override
    def __getitem__(self, index):
        return self.storage[index]

    @override
    def __setitem__(self, index, value):
        self.storage[index] = value

    @override
    def __delitem__(self, index):
        del self.storage[index]

    @override
    def insert(self, index, value):
        self.storage.insert(index, value)


class ListStorage(SequenceStorage):

    @default
    @instance_property
    def storage(self):
        return list()

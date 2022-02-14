# -*- coding: utf-8 -*-
from node.interfaces import IOrdered
from node.interfaces import IMappingStorage
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


# B/C 2022-02-14
Storage = MappingStorage


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

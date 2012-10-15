from odict import odict
from plumber import (
    default,
    override,
    Behavior,
)
from zope.interface import implementer
from ..interfaces import (
    IStorage,
    IOrdered,
)
from ..utils import instance_property


@implementer(IStorage)
class Storage(Behavior):

    @default
    @property
    def storage(self):
        raise NotImplementedError(u"Abstract storage does not implement "
                                  u"``storage``")

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


class DictStorage(Storage):

    @default
    @instance_property
    def storage(self):
        return dict()


@implementer(IOrdered)
class OdictStorage(Storage):

    @default
    @instance_property
    def storage(self):
        return odict()

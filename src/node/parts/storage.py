from odict import odict
from plumber import (
    default,
    extend,
    Part,
)
from node.interfaces import IStorage
from node.utils import instance_property
from zope.interface import implements


class Storage(Part):
    implements(IStorage)
    
    @default
    @property
    def storage(self):
        raise NotImplementedError(u"Abstract storage does not implement "
                                  u"``storage``")
    
    @extend
    def __getitem__(self, key):
        return self.storage[key]
    
    @extend
    def __delitem__(self, key):
        del self.storage[key]
    
    @extend
    def __setitem__(self, key, val):
        self.storage[key] = val
    
    @extend
    def __iter__(self):
        return self.storage.__iter__()


class DictStorage(Storage):
    
    @default
    @instance_property
    def storage(self):
        return dict()


class OdictStorage(Storage):
    
    @default
    @instance_property
    def storage(self):
        return odict()
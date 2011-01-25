from odict import odict
from plumber import (
    default,
    extend,
    Part,
)


class DictStorage(Part):
    
    @default
    @property
    def storage(self):
        if not hasattr(self, '_storage_data'):
            self._storage_data = dict()
        return self._storage_data
    
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


class OdictStorage(Part):
    
    @default
    @property
    def storage(self):
        if not hasattr(self, '_storage_data'):
            self._storage_data = odict()
        return self._storage_data
    
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
    
    @extend
    def popitem(self):
        return self.storage.popitem()

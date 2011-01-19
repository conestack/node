from plumber import (
    plumb,
    extend,
    default,
)
from zope.interface import implements
from node.interfaces import IReference

class NodeIndex(object):
    implements(IReadMapping)

    def __init__(self, index):
        self._index = index

    def __getitem__(self, key):
        return self._index[int(key)]

    def get(self, key, default=None):
        return self._index.get(int(key), default)

    def __contains__(self, key):
        return int(key) in self._index

class Reference(object):

    def __init__(self, name=None, index=True):
        self._index = dict()
        self._uuid = None
        self.uuid = uuid.uuid4()
    
    def _adopt(self, key, val):
        """Adopting happens eg during ``__setitem__``.
        """
        has_children = False
        for valkey in val.iterkeys():
            has_children = True
            break
        if has_children:
            keys = set(self._index.keys())
            if keys.intersection(val._index.keys()):
                raise ValueError, u"Node with uuid already exists"
        self._index.update(val._index)
        val._index = self._index
    
    def __setitem__(self, key, val):
        if isinstance(val, _Node):
            self._adopt(key, val)
        self._node_impl().__setitem__(self, key, val)
    
    def __delitem__(self, key):
        # fail immediately if key does not exist
        self[key]
        for iuuid in self[key]._to_delete():
            del self._index[iuuid]
        self._node_impl().__delitem__(self, key)
    
    def _get_uuid(self):
        return self._uuid

    def _set_uuid(self, uuid):
        iuuid = uuid is not None and int(uuid) or None
        if iuuid in self._index \
          and self._index[iuuid] is not self:
            raise ValueError, u"Given uuid was already used for another Node"
        siuuid = self._uuid is not None and int(self._uuid) or None
        if siuuid in self._index:
            del self._index[siuuid]
        self._index[iuuid] = self
        self._uuid = uuid

    uuid = property(_get_uuid, _set_uuid)
    
    @property
    def index(self):
        return NodeIndex(self._index)

    def node(self, uuid):
        return self._index.get(int(uuid))
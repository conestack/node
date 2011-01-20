import uuid
from plumber import (
    plumb,
    extend,
    default,
    Part,
)
from zope.interface import implements
from zope.interface.common.mapping import IReadMapping
from node.interfaces import (
    INode,
    IReference,
)

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

class Reference(Part):

    @plumb
    def __init__(plb, _next, self, *args, **kw):
        self._index = dict()
        self._uuid = None
        self.uuid = uuid.uuid4()
        _next(self, *args, **kw)
    
    @plumb
    def __setitem__(plb, _next, self, key, val):
        if INode.providedBy(val):
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
        _next(self, key, val)
    
    @plumb
    def __delitem__(plb, _next, self, key):
        # fail immediately if key does not exist
        self[key]
        for iuuid in self[key]._to_delete():
            del self._index[iuuid]
        _next(self, key)
    
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

    uuid = extend(property(_get_uuid, _set_uuid))
    
    @extend
    @property
    def index(self):
        return NodeIndex(self._index)

    @extend
    def node(self, uuid):
        return self._index.get(int(uuid))
    
    @default
    def _to_delete(self):
        todel = [int(self.uuid)]
        for childkey in self:
            try:
                todel += self[childkey]._to_delete()
            except AttributeError:
                # Non-Node values or non referencing children are not told
                # about deletion.
                continue
        return todel

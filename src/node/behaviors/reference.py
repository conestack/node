# -*- coding: utf-8 -*-
from node.interfaces import INode
from node.interfaces import IReference
from plumber import Behavior
from plumber import default
from plumber import override
from plumber import plumb
from zope.interface import implementer
from zope.interface.common.mapping import IReadMapping
import uuid


@implementer(IReadMapping)
class NodeIndex(object):

    def __init__(self, index):
        self._index = index

    def __getitem__(self, key):
        return self._index[int(key)]

    def get(self, key, default=None):
        return self._index.get(int(key), default)

    def __contains__(self, key):
        return int(key) in self._index


@implementer(IReference)
class Reference(Behavior):
    _uuid = default(None)

    @plumb
    def __init__(_next, self, *args, **kw):
        self._index = dict()
        self.uuid = uuid.uuid4()
        _next(self, *args, **kw)

    @plumb
    def __setitem__(_next, self, key, val):
        if INode.providedBy(val):
            try:
                next(val.iterkeys())
                keys = set(self._index.keys())
                if keys.intersection(val._index.keys()):
                    raise ValueError('Node with uuid already exists')
            except StopIteration:
                pass
            self._index.update(val._index)
            val._index = self._index
        _next(self, key, val)

    @plumb
    def __delitem__(_next, self, key):
        # fail immediately if key does not exist
        todel = self[key]
        if hasattr(todel, '_to_delete'):
            for iuuid in todel._to_delete():
                del self._index[iuuid]
        _next(self, key)

    @plumb
    def detach(_next, self, key):
        node = _next(self, key)
        node._index = {int(node.uuid): node}
        node._index_nodes()
        return node

    @property
    def uuid(self):
        return self._uuid

    @override
    @uuid.setter
    def uuid(self, uuid):
        iuuid = uuid is not None and int(uuid) or None
        if iuuid in self._index \
                and self._index[iuuid] is not self:
            raise ValueError('Given uuid was already used for another Node')
        siuuid = self._uuid is not None and int(self._uuid) or None
        if siuuid in self._index:
            del self._index[siuuid]
        self._index[iuuid] = self
        self._uuid = uuid

    @override
    @property
    def index(self):
        return NodeIndex(self._index)

    @override
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

    @default
    def _index_nodes(self):
        for node in self.values():
            try:
                uuid = int(node.uuid)
            except AttributeError:
                # non-Node values are a dead end, no magic for them
                continue
            self._index[uuid] = node
            node._index = self._index
            node._index_nodes()

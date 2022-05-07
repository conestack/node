from __future__ import absolute_import
from node.interfaces import IMappingNode
from node.interfaces import IMappingReference
from node.interfaces import INodeReference
from node.interfaces import ISequenceNode
from node.interfaces import ISequenceReference
from plumber import Behavior
from plumber import default
from plumber import override
from plumber import plumb
from plumber import plumbifexists
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


class IndexViolationError(ValueError):

    def __init__(self, message, colliding):
        super(IndexViolationError, self).__init__(message)
        self.message = message
        self.colliding = [uuid.UUID(int=iuuid) for iuuid in colliding]

    def __repr__(self):
        return 'Index Violation: {}\n  * {}'.format(
            self.message,
            '\n  * '.join([str(uuid_) for uuid_ in self.colliding])
        )


@implementer(INodeReference)
class NodeReference(Behavior):
    _uuid = default(None)

    @plumb
    def __init__(next_, self, *args, **kw):
        self._index = dict()
        self.uuid = uuid.uuid4()
        next_(self, *args, **kw)

    @property
    def uuid(self):
        return self._uuid

    @override
    @uuid.setter
    def uuid(self, uuid):
        index = self._index
        iuuid = None if uuid is None else int(uuid)
        if iuuid in index and index[iuuid] is not self:
            raise IndexViolationError(
                'Given uuid was already used for another Node',
                [iuuid]
            )
        siuuid = None if self._uuid is None else int(self._uuid)
        if siuuid in index:
            del index[siuuid]
        index[iuuid] = self
        self._uuid = uuid

    @override
    @property
    def index(self):
        return NodeIndex(self._index)

    @override
    def node(self, uuid):
        return self._index.get(int(uuid))

    @plumbifexists
    def __setitem__(next_, self, name, value):
        # works on mapping and sequence nodes
        self._update_reference_index(value)
        next_(self, name, value)

    @plumbifexists
    def __delitem__(next_, self, name):
        # works on mapping and sequence nodes
        # fail immediately if name does not exist
        value = self[name]
        self._reduce_reference_index(value)
        next_(self, name)

    @plumb
    def detach(next_, self, key):
        node = next_(self, key)
        iuuid = int(node.uuid)
        node._index = {iuuid: node}
        node._init_reference_index()
        return node

    @default
    @property
    def _referencable_child_nodes(self):
        children = []
        if IMappingNode.providedBy(self):
            children = self.values()
        elif ISequenceNode.providedBy(self):
            children = self
        for child in children:
            if INodeReference.providedBy(child):
                yield child

    @default
    @property
    def _recursiv_reference_keys(self):
        keys = [int(self.uuid)]
        for node in self._referencable_child_nodes:
            keys += node._recursiv_reference_keys
        return keys

    @default
    def _init_reference_index(self):
        for node in self._referencable_child_nodes:
            self._index[int(node.uuid)] = node
            node._index = self._index
            node._init_reference_index()

    @default
    def _update_reference_index(self, value):
        if INodeReference.providedBy(value):
            index = self._index
            colliding = set(index).intersection(value._index)
            if colliding:
                raise IndexViolationError(
                    'Node with uuid(s) already exist in tree',
                    colliding
                )
            index.update(value._index)
            def _set_index(node):
                node._index = index
                for child in node._referencable_child_nodes:
                    _set_index(child)
            _set_index(value)

    @default
    def _reduce_reference_index(self, value):
        if INodeReference.providedBy(value):
            index = self._index
            for iuuid in value._recursiv_reference_keys:
                del index[iuuid]

    @plumbifexists
    def _validateinsertion(next_, self, node):
        # case Order behavior applied
        next_(self, node)
        if self.node(node.uuid) is not None:
            raise KeyError('Given node already contained in tree.')


@implementer(IMappingReference)
class MappingReference(NodeReference):
    pass


@implementer(ISequenceReference)
class SequenceReference(NodeReference):

    @plumb
    def insert(next_, self, index, value):
        self._update_reference_index(value)
        next_(self, index, value)

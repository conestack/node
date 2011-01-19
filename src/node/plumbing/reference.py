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
        self._adopting = True
        if index:
            self._index = dict()
            self._uuid = None
            self.uuid = uuid.uuid4()
        else:
            self._index = None
    
    def _adopt(self, key, val):
        """Adopting happens eg during ``__setitem__``.
        """
        # remember val __name__ and __parent__ for reverting
        old__name__ = val.__name__
        old__parent__ = val.__parent__
        # immediately set __name__ and __parent__ on val, implementation often
        # require hierarchy information to acquire keys
        val.__name__ = key
        val.__parent__ = self
        has_children = False
        # XXX: maybe skip this check and just use self._index for condition in
        #      next code block. then remembering origin __name__ and __parent__
        #      gets obsolete
        if self._index is not None:
            # XXX: this iterkeys was a problem with the current LDAPNode's
            # __setitem__. As we don't have indexing on them we circumvented
            # the problem.
            for valkey in val.iterkeys():
                has_children = True
                break
            if has_children:
                keys = set(self._index.keys())
                if keys.intersection(val._index.keys()):
                    val.__name__ = old__name__
                    val.__parent__ = old__parent__
                    raise ValueError, u"Node with uuid already exists"
            self._index.update(val._index)
            val._index = self._index
    
    def __setitem__(self, key, val):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            if isinstance(val, _Node):
                val.__name__ = key
                val.__parent__ = self
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            self.nodespaces[key] = val
            # index checks below must not happen for other nodespace.
            return
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if isinstance(val, _Node):
            if self._adopting:
                self._adopt(key, val)
        else:
            if not self.allow_non_node_childs:
                raise ValueError("Non-node childs are not allowed.")
        self._node_impl().__setitem__(self, key, val)
    
    def __delitem__(self, key):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            del self.nodespaces[key]
            return
        # fail immediately if key does not exist
        self[key]
        if self._index is not None:
            for iuuid in self[key]._to_delete():
                del self._index[iuuid]
        self._node_impl().__delitem__(self, key)
    
    def _get_uuid(self):
        return self._uuid

    def _set_uuid(self, uuid):
        iuuid = uuid is not None and int(uuid) or None
        if self._index is not None \
          and iuuid in self._index \
          and self._index[iuuid] is not self:
            raise ValueError, u"Given uuid was already used for another Node"
        siuuid = self._uuid is not None and int(self._uuid) or None
        if self._index is not None and siuuid in self._index:
            del self._index[siuuid]
        if self._index is not None:
            self._index[iuuid] = self
        self._uuid = uuid

    uuid = property(_get_uuid, _set_uuid)
    
    @property
    def index(self):
        if self._index is None:
            raise AttributeError(u"No index support configured on this Node.")
        return NodeIndex(self._index)

    def node(self, uuid):
        if self._index is None:
            raise ValueError(u"No index support configured on this Node.")
        return self._index.get(int(uuid))
# -*- coding: utf-8 -*-
from node.interfaces import IOrder
from odict.pyodict import _nil
from plumber import Behavior
from plumber import override
from zope.interface import implementer


@implementer(IOrder)
class Order(Behavior):

    @override
    def swap(self, node_a, node_b):
        dict_impl = self.storage._dict_impl()
        orgin_a = dict_impl.__getitem__(self.storage, node_a.name)
        orgin_b = dict_impl.__getitem__(self.storage, node_b.name)
        new_a = [orgin_b[0], orgin_a[1], orgin_b[2]]
        new_b = [orgin_a[0], orgin_b[1], orgin_a[2]]
        if new_a[0] == new_a[1].name:
            new_a[0] = new_b[1].name
            new_b[2] = new_a[1].name
        if new_b[0] == new_b[1].name:
            new_b[0] = new_a[1].name
            new_a[2] = new_b[1].name
        if new_a[0] != _nil:
            dict_impl.__getitem__(self.storage, new_a[0])[2] = new_a[1].name
        if new_a[2] != _nil:
            dict_impl.__getitem__(self.storage, new_a[2])[0] = new_a[1].name
        if new_b[0] != _nil:
            dict_impl.__getitem__(self.storage, new_b[0])[2] = new_b[1].name
        if new_b[2] != _nil:
            dict_impl.__getitem__(self.storage, new_b[2])[0] = new_b[1].name
        dict_impl.__setitem__(self.storage, new_a[1].name, new_a)
        dict_impl.__setitem__(self.storage, new_b[1].name, new_b)
        if new_a[0] == _nil:
            self.storage.lh = new_a[1].name
        if new_a[2] == _nil:
            self.storage.lt = new_a[1].name
        if new_b[0] == _nil:
            self.storage.lh = new_b[1].name
        if new_b[2] == _nil:
            self.storage.lt = new_b[1].name

    @override
    def insertfirst(self, newnode):
        keys = self.keys()
        if not keys:
            self[newnode.name] = newnode
            return
        refnode = self[keys[0]]
        self.insertbefore(newnode, refnode)

    @override
    def insertlast(self, newnode):
        keys = self.keys()
        if not keys:
            self[newnode.name] = newnode
            return
        refnode = self[keys[-1]]
        self.insertafter(newnode, refnode)

    @override
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        prevnode = None
        prevkey = None
        storage = self.storage
        dict_impl = storage._dict_impl()
        if index > 0:
            prevkey = self.keys()[index - 1]
            prevnode = dict_impl.__getitem__(storage, prevkey)
        if prevnode is not None:
            dict_impl.__getitem__(storage, prevkey)[2] = nodekey
            newnode = [prevkey, newnode, refkey]
        else:
            storage.lh = nodekey
            newnode = [_nil, newnode, refkey]
        dict_impl.__getitem__(storage, refkey)[0] = nodekey
        dict_impl.__setitem__(storage, nodekey, newnode)
        self[nodekey] = newnode[1]

    @override
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        nextnode = None
        nextkey = None
        keys = self.keys()
        storage = self.storage
        dict_impl = storage._dict_impl()
        if index < len(keys) - 1:
            nextkey = self.keys()[index + 1]
            nextnode = dict_impl.__getitem__(storage, nextkey)
        if nextnode is not None:
            dict_impl.__getitem__(storage, nextkey)[0] = nodekey
            newnode = [refkey, newnode, nextkey]
        else:
            storage.lt = nodekey
            newnode = [refkey, newnode, _nil]
        dict_impl.__getitem__(storage, refkey)[2] = nodekey
        dict_impl.__setitem__(storage, nodekey, newnode)
        self[nodekey] = newnode[1]

    @override
    def _validateinsertion(self, newnode, refnode):
        nodekey = newnode.__name__
        if nodekey is None:
            raise ValueError('Given node has no __name__ set.')
        # case if Reference behavior is mixed in
        # XXX: move out of here
        if hasattr(self, 'node'):
            if self.node(newnode.uuid) is not None:
                raise KeyError('Given node already contained in tree.')
        index = self._nodeindex(refnode)
        if index is None:
            raise ValueError('Given reference node not child of self.')

    @override
    def _nodeindex(self, node):
        index = 0
        for key in self.keys():
            if key == node.__name__:
                return index
            index += 1
        return None

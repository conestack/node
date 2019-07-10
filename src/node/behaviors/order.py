# -*- coding: utf-8 -*-
from node.interfaces import IOrder
from plumber import Behavior
from plumber import override
from zope.interface import implementer


@implementer(IOrder)
class Order(Behavior):

    @override
    def swap(self, node_a, node_b):
        self.storage.swap(node_a.name, node_b.name)

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
        self._validateinsertion(newnode)
        try:
            self.storage.insertbefore(refnode.name, newnode.name, newnode)
        except KeyError:
            raise ValueError('Given reference node not child of self.')
        self[newnode.name] = newnode

    @override
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode)
        try:
            self.storage.insertafter(refnode.name, newnode.name, newnode)
        except KeyError:
            raise ValueError('Given reference node not child of self.')
        self[newnode.name] = newnode

    @override
    def _validateinsertion(self, node):
        if node.name is None:
            raise ValueError('Given node has no __name__ set.')
        # case if Reference behavior is mixed in
        # XXX: move out of here
        if hasattr(self, 'node'):
            if self.node(node.uuid) is not None:
                raise KeyError('Given node already contained in tree.')

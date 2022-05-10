from __future__ import absolute_import
from node.interfaces import IOrder
from plumber import Behavior
from plumber import override
from zope.interface import implementer


@implementer(IOrder)
class Order(Behavior):

    @override
    @property
    def first_key(self):
        return self.storage.first_key

    @override
    @property
    def last_key(self):
        return self.storage.last_key

    @override
    def next_key(self, key):
        return self.storage.next_key(key)

    @override
    def prev_key(self, key):
        return self.storage.prev_key(key)

    @override
    def swap(self, node_a, node_b):
        self.storage.swap(node_a.name, node_b.name)

    @override
    def insertfirst(self, newnode):
        self._validateinsertion(newnode)
        self[newnode.name] = newnode
        self.storage.movefirst(newnode.name)

    @override
    def insertlast(self, newnode):
        self._validateinsertion(newnode)
        self[newnode.name] = newnode
        self.storage.movelast(newnode.name)

    @override
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode)
        try:
            self.storage[refnode.name]
            self[newnode.name] = newnode
            self.storage.movebefore(refnode.name, newnode.name)
        except KeyError:
            raise ValueError('Given reference node not child of self.')

    @override
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode)
        try:
            self.storage[refnode.name]
            self[newnode.name] = newnode
            self.storage.moveafter(refnode.name, newnode.name)
        except KeyError:
            raise ValueError('Given reference node not child of self.')

    @override
    def _validateinsertion(self, node):
        name = node.name
        if name is None:
            raise ValueError('Given node has no __name__ set.')
        if name in self.storage:
            raise KeyError(
                'Tree already contains node with name {}'.format(name)
            )

from __future__ import absolute_import
from node.interfaces import INode
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
        name_a = node_a.name if INode.providedBy(node_a) else node_a
        name_b = node_b.name if INode.providedBy(node_b) else node_b
        self.storage.swap(name_a, name_b)

    @override
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode)
        newnode_name = newnode.name
        refnode_name = refnode.name if INode.providedBy(refnode) else refnode
        try:
            self.storage[refnode_name]
            self[newnode_name] = newnode
            self.storage.movebefore(refnode_name, newnode_name)
        except KeyError:
            raise ValueError('Given reference node not child of self.')

    @override
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode)
        newnode_name = newnode.name
        refnode_name = refnode.name if INode.providedBy(refnode) else refnode
        try:
            self.storage[refnode_name]
            self[newnode_name] = newnode
            self.storage.moveafter(refnode_name, newnode_name)
        except KeyError:
            raise ValueError('Given reference node not child of self.')

    @override
    def insertfirst(self, newnode):
        self._validateinsertion(newnode)
        newnode_name = newnode.name
        self[newnode_name] = newnode
        self.storage.movefirst(newnode_name)

    @override
    def insertlast(self, newnode):
        self._validateinsertion(newnode)
        newnode_name = newnode.name
        self[newnode_name] = newnode
        self.storage.movelast(newnode_name)

    @override
    def movebefore(self, movenode, refnode):
        movenode_name = movenode.name if INode.providedBy(movenode) else movenode
        refnode_name = refnode.name if INode.providedBy(refnode) else refnode
        self.storage.movebefore(refnode_name, movenode_name)

    @override
    def moveafter(self, movenode, refnode):
        movenode_name = movenode.name if INode.providedBy(movenode) else movenode
        refnode_name = refnode.name if INode.providedBy(refnode) else refnode
        self.storage.moveafter(refnode_name, movenode_name)

    @override
    def movefirst(self, movenode):
        movenode_name = movenode.name if INode.providedBy(movenode) else movenode
        self.storage.movefirst(movenode_name)

    @override
    def movelast(self, movenode):
        movenode_name = movenode.name if INode.providedBy(movenode) else movenode
        self.storage.movelast(movenode_name)

    @override
    def _validateinsertion(self, node):
        name = node.name
        if name is None:
            raise ValueError('Given node has no __name__ set.')
        if name in self.storage:
            raise KeyError(
                'Tree already contains node with name {}'.format(name)
            )

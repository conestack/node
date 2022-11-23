from __future__ import absolute_import
from node.interfaces import IMappingOrder
from node.interfaces import INode
from node.interfaces import ISequenceOrder
from plumber import Behavior
from plumber import override
from zope.interface import implementer


@implementer(IMappingOrder)
class MappingOrder(Behavior):

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
            msg = 'Tree already contains node with name {}'.format(name)
            raise KeyError(msg)


@implementer(ISequenceOrder)
class SequenceOrder(Behavior):

    @override
    @property
    def first_index(self):
        if not self.storage:
            raise IndexError('Sequence is empty')
        return 0

    @override
    @property
    def last_index(self):
        if not self.storage:
            raise IndexError('Sequence is empty')
        return len(self.storage) - 1

    @override
    def next_index(self, index):
        index += 1
        if index > self.last_index:
            raise IndexError('No next index')
        return index

    @override
    def prev_index(self, index):
        index -= 1
        if index < self.first_index:
            raise IndexError('No previous index')
        return index

    @override
    def swap(self, node_a, node_b):
        index_a = self._lookup_node_index(node_a)
        index_b = self._lookup_node_index(node_b)
        storage = self.storage
        storage[index_a], storage[index_b] = storage[index_b], storage[index_a]
        self._update_indices()

    @override
    def insertbefore(self, newnode, refnode):
        if newnode in self:
            raise ValueError('Given node already child of self.')
        ref_index = self._lookup_node_index(refnode)
        self.insert(ref_index, newnode)

    @override
    def insertafter(self, newnode, refnode):
        if newnode in self:
            raise ValueError('Given node already child of self.')
        ref_index = self._lookup_node_index(refnode)
        self.insert(ref_index + 1, newnode)

    @override
    def insertfirst(self, newnode):
        if newnode in self:
            raise ValueError('Given node already child of self.')
        self.insert(0, newnode)

    @override
    def insertlast(self, newnode):
        if newnode in self:
            raise ValueError('Given node already child of self.')
        self.append(newnode)

    @override
    def movebefore(self, movenode, refnode):
        move_index = self._lookup_node_index(movenode)
        ref_index = self._lookup_node_index(refnode)
        storage = self.storage
        move_val = storage[move_index]
        storage.insert(ref_index, move_val)
        if ref_index > move_index:
            del storage[move_index]
        else:
            del storage[move_index + 1]
        self._update_indices()

    @override
    def moveafter(self, movenode, refnode):
        move_index = self._lookup_node_index(movenode)
        ref_index = self._lookup_node_index(refnode)
        storage = self.storage
        move_val = storage[move_index]
        storage.insert(ref_index + 1, move_val)
        if ref_index > move_index:
            del storage[move_index]
        else:
            del storage[move_index + 1]
        self._update_indices()

    @override
    def movefirst(self, movenode):
        move_index = self._lookup_node_index(movenode)
        storage = self.storage
        move_val = storage[move_index]
        del storage[move_index]
        storage.insert(0, move_val)
        self._update_indices()

    @override
    def movelast(self, movenode):
        move_index = self._lookup_node_index(movenode)
        storage = self.storage
        move_val = storage[move_index]
        del storage[move_index]
        storage.append(move_val)
        self._update_indices()

    @override
    def _lookup_node_index(self, node):
        storage = self.storage
        try:
            if INode.providedBy(node):
                index = int(node.name)
            else:
                index = int(node)
            if index < 0 or index + 1 > len(storage):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('Given reference node not child of self.')
        return index

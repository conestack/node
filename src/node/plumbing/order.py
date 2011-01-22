from odict.pyodict import _nil
from plumber import (
    extend,
    default,
    Part,
)
from zope.interface import implements
from zope.interface.common.mapping import IReadMapping
from node.interfaces import (
    INode,
    IReference,
    IOrder,
)

class Order(Part):
    implements(IOrder)

    @extend
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        prevnode = None
        prevkey = None
        if index > 0:
            prevkey = self.keys()[index - 1]
            prevnode = self._dict_impl().__getitem__(self, prevkey)
        if prevnode is not None:
            self._dict_impl().__getitem__(self, prevkey)[2] = nodekey
            newnode = [prevkey, newnode, refkey]
        else:
            self.lh = nodekey
            newnode = [_nil, newnode, refkey]
        self._dict_impl().__getitem__(self, refkey)[0] = nodekey
        self._dict_impl().__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]

    @extend
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        nextnode = None
        nextkey = None
        keys = self.keys()
        if index < len(keys) - 1:
            nextkey = self.keys()[index + 1]
            nextnode = self._dict_impl().__getitem__(self, nextkey)
        if nextnode is not None:
            self._dict_impl().__getitem__(self, nextkey)[0] = nodekey
            newnode = [refkey, newnode, nextkey]
        else:
            self.lt = nodekey
            newnode = [refkey, newnode, _nil]
        self._dict_impl().__getitem__(self, refkey)[2] = nodekey
        self._dict_impl().__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]
    
    @extend
    def _validateinsertion(self, newnode, refnode):
        nodekey = newnode.__name__
        if nodekey is None:
            raise ValueError, u"Given node has no __name__ set."
        # case if Reference Part is mixed in
        # XXX: move out of here
        if hasattr(self, 'node'):
            if self.node(newnode.uuid) is not None:
                raise KeyError, u"Given node already contained in tree."
        index = self._nodeindex(refnode)
        if index is None:
            raise ValueError, u"Given reference node not child of self."

    @extend
    def _nodeindex(self, node):
        index = 0
        for key in self.keys():
            if key == node.__name__:
                return index
            index += 1
        return None

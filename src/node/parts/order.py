from odict.pyodict import _nil
from plumber import (
    extend,
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

    @extend
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

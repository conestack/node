from zope.interface import implements
from odict.pyodict import _nil
from node.interfaces import IOrderable
from node.meta import (
    behavior,
    before,
    after,
    BaseBehavior,
)

class Orderable(BaseBehavior):
    """Only works with odict based nodes, depends on internal double linked
    list implementation.
    """
    
    implements(IOrderable)
    
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        
        #if nodekey == 'child4':
        #    import pdb;pdb.set_trace()
        
        index = self._nodeindex(refnode)
        prevnode = None
        prevkey = None
        dict_impl = self.context._dict_impl()
        if index > 0:
            prevkey = self.context.keys()[index - 1]
            prevnode = dict_impl.__getitem__(self.context.context, prevkey)
        if prevnode is not None:
            dict_impl.__getitem__(self.context.context, prevkey)[2] = nodekey
            newnode = [prevkey, newnode, refkey]
        else:
            self.context.lh = nodekey
            newnode = [_nil, newnode, refkey]
        dict_impl.__getitem__(self.context.context, refkey)[0] = nodekey
        dict_impl.__setitem__(self.context.context, nodekey, newnode)
        
        # XXX: fails??
        #setitem = self.context.context.__class__._wrapped.__setitem__
        #setitem = self.context.context.__class__.__setitem__
        #setitem(self.context.context, nodekey, newnode[1])
        self.context[nodekey] = newnode[1]
    
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        nextnode = None
        nextkey = None
        keys = self.context.keys()
        dict_impl = self.context._dict_impl()
        if index < len(keys) - 1:
            nextkey = self.context.keys()[index + 1]
            nextnode = dict_impl.__getitem__(self.context.context, nextkey)
        if nextnode is not None:
            dict_impl.__getitem__(self.context.context, nextkey)[0] = nodekey
            newnode = [refkey, newnode, nextkey]
        else:
            self.context.lt = nodekey
            newnode = [refkey, newnode, _nil]
        dict_impl.__getitem__(self.context.context, refkey)[2] = nodekey
        dict_impl.__setitem__(self.context.context, nodekey, newnode)
        self.context[nodekey] = newnode[1]
    
    def detach(self, key):
        node = self.context[key]
        del self.context[key]
        #if self._index is not None:
        #    # XXX: before handler in IReferenced
        #    node._index = { int(node.uuid): node }
        #    node._index_nodes()
        return node
    
    def _validateinsertion(self, newnode, refnode):
        nodekey = newnode.__name__
        if nodekey is None:
            raise ValueError, u"Given node has no __name__ set."
        #if self.node(newnode.uuid) is not None:
        #    raise KeyError, u"Given node already contained in tree."
        index = self._nodeindex(refnode)
        if index is None:
            raise ValueError, u"Given reference node not child of self."
    
    def _nodeindex(self, node):
        index = 0
        for key in self.context.keys():
            if key == node.__name__:
                return index
            index += 1
        return None
    
    #def _index_nodes(self):
    #    # XXX: before handler in IReferenced
    #    for node in self.values():
    #        try:
    #            uuid = int(node.uuid)
    #        except AttributeError:
    #            # non-Node values are a dead end, no magic for them
    #            continue
    #        self._index[uuid] = node
    #        node._index = self._index
    #        node._index_nodes()
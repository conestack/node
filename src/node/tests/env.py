import inspect
from odict import odict as somefullmapping
from node.interfaces import INode
from node.base import AbstractNode


class MyNode(AbstractNode, somefullmapping):
    """Subclass ``AbstractNode`` and provide needed functions.
    
    Below we utilize ``odict.odict`` for most of the work. There exists node 
    ``OrderedNode``, which already uses odict, so for illustration we import
    ``odict`` as ``somefullmapping``.
    """
    
    def __init__(self, name=None, parent=None):
        # XXX: using ``super`` on dedicated base class? how?
        somefullmapping.__init__(self)
        AbstractNode.__init__(self, name, parent)
    
    __getitem__ = somefullmapping.__getitem__
    
    __delitem__ = somefullmapping.__delitem__
    
    def __setitem__(self, key, val):
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if not self.allow_non_node_childs and not INode.providedBy(val):
            raise ValueError("Non-node childs are not allowed.")
        if INode.providedBy(val):
            val.__name__ = key
            val.__parent__ = self
        somefullmapping.__setitem__(self, key, val)
    
    __iter__ = somefullmapping.__iter__
    
    clear = somefullmapping.clear
    
    update = somefullmapping.update
    
    setdefault = somefullmapping.setdefault
    
    pop = somefullmapping.pop
    
    popitem = somefullmapping.popitem

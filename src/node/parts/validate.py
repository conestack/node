import inspect
from plumber import (
    plumb,
    default,
    Part,
)
from zope.interface import implements
from node.interfaces import (
    INode,
    INodeChildValidate,
)

class NodeChildValidate(Part):
    implements(INodeChildValidate)
    
    allow_non_node_childs = default(False)
    
    @plumb
    def __setitem__(_next, self, key, val):
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if not self.allow_non_node_childs and not INode.providedBy(val):
            raise ValueError("Non-node childs are not allowed.")
        _next(self, key, val)

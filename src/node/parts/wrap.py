from plumber import (
    plumb,
    Part,
)
from node.interfaces import INode


class Wrap(Part):
    """Plumbing element that wraps nodes coming from deeper levels in a 
    NodeNode.
    """
    
    @plumb
    def __getitem__(plb, _next, self, key):
        val = _next(self, key)
        if INode.providedBy(val):
            val = NodeNode(val)
        return val

    @plumb
    def __setitem__(plb, _next, self, key, val):
        if INode.providedBy(val):
            val = val.context
        _next(self, key, val)

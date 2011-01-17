from plumber import plumbing
from node.interfaces import INode


class Wrap(object):
    """Plumbing element that wraps nodes coming from deeper levels in a NodeNode
    """
    @plumbing
    def __getitem__(cls, _next, self, key):
        val = _next(self, key)
        if INode.providedBy(val):
            val = NodeNode(val)
        return val

    @plumbing
    def __setitem__(cls, _next, self, key, val):
        if INode.providedBy(val):
            val = val.context
        _next(self, key, val)

from odict import odict
from plumber import Plumber
from zope.interface import implements
from node.interfaces import INode
from node.plumbing.adopt import Adopt
from node.plumbing.validate import NodeChildValidate
from node.mixin import (
    _NodeMixin,
    _FullMappingMixin,
    _ImplMixin,
)

class AbstractNode(_NodeMixin, _FullMappingMixin):
    """An abstract Node.
    
    Derive this if you like to implement all storage related functions on your
    own.
    """
    implements(INode)


class BaseNode(_NodeMixin, _ImplMixin, dict):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    __metaclass__ = Plumber
    __pipeline__ = NodeChildValidate, Adopt
    
    implements(INode)
    
    def _mapping_impl(self):
        return dict
    
    def update(self, data=(), **kw):
        for key, value in data:
            self[key] = value
        for key, value in kw.items():
            self[key] = value
    
    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value


class OrderedNode(_NodeMixin, _ImplMixin, odict):
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    __metaclass__ = Plumber
    __pipeline__ = NodeChildValidate, Adopt
    
    implements(INode)
    
    def _mapping_impl(self):
        return odict

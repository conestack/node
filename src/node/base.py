from odict import odict
from plumber import plumber
from zope.interface import implements

from node.interfaces import INode
from node.parts.adopt import Adopt
from node.parts.nodify import Nodify
from node.parts.validate import NodeChildValidate
from node.mixin import _ImplMixin


class BaseNode(_ImplMixin, dict):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = NodeChildValidate, Adopt, Nodify
    
    def _mapping_impl(self):
        return dict


class OrderedNode(_ImplMixin, odict):
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = NodeChildValidate, Adopt, Nodify
    
    def _mapping_impl(self):
        return odict

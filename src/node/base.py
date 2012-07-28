from odict import odict
from plumber import plumber
from node.interfaces import INode
from node.behaviors import Adopt
from node.behaviors import Nodespaces
from node.behaviors import Attributes
from node.behaviors import Reference
from node.behaviors import Order
from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import NodeChildValidate
from node.behaviors import DictStorage
from node.behaviors import OdictStorage


class AbstractNode(object):
    __metaclass__ = plumber
    __plumbing__ = (
        Adopt,
        Nodify,
    )


class BaseNode(object):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        DictStorage,
    )


class OrderedNode(object):
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        OdictStorage,
    )


class Node(object):
    """A node with original functionality from zodict.node.Node.
    
    XXX: reduce by attributes
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Nodespaces,
        Adopt,
        Attributes,
        Reference,
        Order,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        OdictStorage,
    )


class AttributedNode(object):
    """A node with original functionality from zodict.node.AttributedNode.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Nodespaces,
        Adopt,
        Attributes,
        Reference,
        Order,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        OdictStorage,
    )
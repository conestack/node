from odict import odict
from plumber import plumber
from plumber import Part
from plumber import default
from plumber import extend
from zope.interface import implements

from node.interfaces import INode
from node.parts.adopt import Adopt
from node.parts.nodify import Nodify
from node.parts.nodify import NodeInit
from node.parts.nodify import NodeRepr
from node.parts.validate import NodeChildValidate
from node.parts.storage import DictStorage
from node.parts.storage import OdictStorage


class AbstractNode(object):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeInit,
        Adopt,
        Nodify,
        NodeRepr,
    )


class BaseNode(object):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeInit,
        NodeChildValidate,
        Adopt,
        Nodify,
        NodeRepr,
        DictStorage,
    )


class OrderedNode(object):
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeInit,
        NodeChildValidate,
        Adopt,
        Nodify,
        NodeRepr,
        OdictStorage,
    )

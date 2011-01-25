from odict import odict
from plumber import (
    plumber,
    Part,
    default,
    extend,
)
from zope.interface import implements
from node.interfaces import INode
from node.parts import (
    Adopt,
    Nodify,
    NodeInit,
    NodeRepr,
    NodeChildValidate,
    DictStorage,
    OdictStorage,
)


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

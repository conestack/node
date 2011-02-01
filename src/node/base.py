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
    AsAttrAccess,
    Nodify,
    NodeChildValidate,
    DictStorage,
    OdictStorage,
)


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
        Nodify,
        DictStorage,
    )
    
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent


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
        Nodify,
        OdictStorage,
    )
    
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent

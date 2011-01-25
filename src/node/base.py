from odict import odict
from plumber import plumber
from plumber import Part
from plumber import default
from plumber import extend
from zope.interface import implements

from node.interfaces import INode
from node.parts.adopt import Adopt
from node.parts.nodify import Nodify
from node.parts.nodify import NodeRepr
from node.parts.validate import NodeChildValidate
from node.parts.storage import DictStorage
from node.parts.storage import OdictStorage


class AbstractNode(object):
    __metaclass__ = plumber
    __plumbing__ = Adopt, Nodify, NodeRepr
    
    def __init__(self, name=None, parent=None):
        #super(self.__class__, self).__init__()
        self.__name__ = name
        self.__parent__ = parent


class BaseNode(object):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = NodeChildValidate, Adopt, Nodify, NodeRepr, DictStorage
    
    def __init__(self, name=None, parent=None):
        #super(self.__class__, self).__init__()
        self.__name__ = name
        self.__parent__ = parent


class OrderedNode():
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    __metaclass__ = plumber
    __plumbing__ = NodeChildValidate, Adopt, Nodify, NodeRepr, OdictStorage
    
    def __init__(self, name=None, parent=None):
        #super(self.__class__, self).__init__()
        self.__name__ = name
        self.__parent__ = parent

import inspect
from plumber import plumber
from zope.interface import implements
from node.interfaces import INode
from node.parts.adopt import Adopt
from node.parts.nodify import Nodify
from node.parts.nodify import NodeRepr
from node.parts.validate import NodeChildValidate
from node.parts.storage import OdictStorage


class MockupNode(object):
    implements(INode)
    __name__ = None
    __parent__ = None


class NoNode(object):
    pass


class MyNode(object):
    """Below we utilize ``odict.odict`` for most of the work. There exists node 
    ``OrderedNode``, which already uses odict, so for illustration we import
    ``odict`` as ``somefullmapping``.
    """
    __metaclass__ = plumber
    __plumbing__ = NodeChildValidate, Adopt, Nodify, NodeRepr, OdictStorage
    
    def __init__(self, name=None, parent=None):
        super(self.__class__, self).__init__()
        self.__name__ = name
        self.__parent__ = parent

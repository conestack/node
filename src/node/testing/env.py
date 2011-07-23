import inspect
from plumber import plumber
from zope.interface import implements
from node.interfaces import INode
from node.parts import (
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    OdictStorage,
)


class MockupNode(object):
    implements(INode)
    __name__ = None
    __parent__ = None


class NoNode(object):
    pass


class MyNode(object):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        DefaultInit,
        Adopt,
        AsAttrAccess,
        Nodify,
        OdictStorage,
    )

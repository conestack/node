import inspect
from plumber import plumber
from zope.interface import implements
from node.interfaces import INode
from node.parts import (
    Adopt,
    AsAttrAccess,
    Nodify,
    NodeInit,
    NodeRepr,
    NodeChildValidate,
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
        NodeInit,
        NodeChildValidate,
        Adopt,
        AsAttrAccess,
        Nodify,
        NodeRepr,
        OdictStorage,
    )

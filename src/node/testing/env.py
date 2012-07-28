import inspect
from plumber import plumber
from zope.interface import implementer
from node.interfaces import INode
from node.behaviors import NodeChildValidate
from node.behaviors import Adopt
from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import OdictStorage


@implementer(INode)
class MockupNode(object):
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

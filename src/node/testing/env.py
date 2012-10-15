from plumber import plumber
from zope.interface import implementer
from ..interfaces import INode
from ..behaviors import (
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    OdictStorage,
)


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

from plumber import plumbing
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


@plumbing(
    NodeChildValidate,
    DefaultInit,
    Adopt,
    AsAttrAccess,
    Nodify,
    OdictStorage)
class MyNode(object):
    pass

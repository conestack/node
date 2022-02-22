from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import MappingAdopt
from node.behaviors import MappingConstraints
from node.behaviors import MappingNode
from node.behaviors import OdictStorage
from node.interfaces import INode
from plumber import plumbing
from zope.interface import implementer


@implementer(INode)
class MockupNode(object):
    __name__ = None
    __parent__ = None


class NoNode(object):
    pass


@plumbing(
    MappingConstraints,
    DefaultInit,
    MappingAdopt,
    AsAttrAccess,
    MappingNode,
    OdictStorage)
class MyNode(object):
    pass

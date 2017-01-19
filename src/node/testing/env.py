# -*- coding: utf-8 -*-
from node.behaviors import Adopt
from node.behaviors import AsAttrAccess
from node.behaviors import DefaultInit
from node.behaviors import NodeChildValidate
from node.behaviors import Nodify
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
    NodeChildValidate,
    DefaultInit,
    Adopt,
    AsAttrAccess,
    Nodify,
    OdictStorage)
class MyNode(object):
    pass

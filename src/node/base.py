# -*- coding: utf-8 -*-
from node.behaviors import Adopt
from node.behaviors import AsAttrAccess
from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import NodeChildValidate
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors import Order
from node.behaviors import Reference
from plumber import plumbing


@plumbing(
    Adopt,
    Nodify)
class AbstractNode(object):
    pass


@plumbing(
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    DictStorage)
class BaseNode(object):
    """Base node, not ordered.

    Uses ``dict`` as ``IFullMapping`` implementation.

    Derive this for unordered trees.
    """


@plumbing(
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    OdictStorage)
class OrderedNode(object):
    """Ordered node.

    Uses ``odict`` as ``IFullMapping`` implementation.

    Derive this for ordered trees.
    """


@plumbing(
    NodeChildValidate,
    Nodespaces,
    Adopt,
    Attributes,
    Reference,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    OdictStorage)
class Node(object):
    """A node with original functionality from zodict.node.Node.

    XXX: reduce by attributes
    """


@plumbing(
    NodeChildValidate,
    Nodespaces,
    Adopt,
    Attributes,
    Reference,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    OdictStorage)
class AttributedNode(object):
    """A node with original functionality from zodict.node.AttributedNode.
    """

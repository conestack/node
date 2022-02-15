# -*- coding: utf-8 -*-
from node.behaviors import Adopt
from node.behaviors import AsAttrAccess
from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import ListStorage
from node.behaviors import MappingNode
from node.behaviors import NodeChildValidate
from node.behaviors import Nodespaces
from node.behaviors import OdictStorage
from node.behaviors import Order
from node.behaviors import Reference
from node.behaviors import SequenceNode
from plumber import plumbing


@plumbing(
    Adopt,
    MappingNode)
class AbstractNode(object):
    pass


@plumbing(
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    DictStorage)
class BaseNode(object):
    """Base node, not ordered.

    Uses ``dict`` as mapping implementation.
    """


@plumbing(
    NodeChildValidate,
    Adopt,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class OrderedNode(object):
    """Ordered node.

    Uses ``odict`` as mapping implementation.
    """


@plumbing(
    DefaultInit,
    SequenceNode,
    ListStorage)
class ListNode(object):
    """Sequence node.

    Uses ``list`` as sequence implementation.
    """


###############################################################################
# B/C from zodict.
# XXX: will be removed soon
###############################################################################

@plumbing(
    NodeChildValidate,
    Nodespaces,
    Adopt,
    Attributes,
    Reference,
    Order,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class Node(object):
    """A node with original functionality from zodict.node.Node."""


@plumbing(
    NodeChildValidate,
    Nodespaces,
    Adopt,
    Attributes,
    Reference,
    Order,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class AttributedNode(object):
    """A node with original functionality from zodict.node.AttributedNode."""

from node.behaviors import AsAttrAccess
from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import ListStorage
from node.behaviors import MappingAdopt
from node.behaviors import MappingConstraints
from node.behaviors import MappingNode
from node.behaviors import MappingReference
from node.behaviors import Nodespaces
from node.behaviors import OdictStorage
from node.behaviors import MappingOrder
from node.behaviors import SequenceAdopt
from node.behaviors import SequenceConstraints
from node.behaviors import SequenceNode
from plumber import plumbing


@plumbing(
    MappingAdopt,
    MappingNode)
class AbstractNode(object):
    pass


@plumbing(
    MappingConstraints,
    MappingAdopt,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    DictStorage)
class BaseNode(object):
    """Base node, not ordered.

    Uses ``dict`` as mapping implementation.
    """


@plumbing(
    MappingConstraints,
    MappingAdopt,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class OrderedNode(object):
    """Ordered node.

    Uses ``odict`` as mapping implementation.
    """


@plumbing(
    SequenceConstraints,
    SequenceAdopt,
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
    MappingConstraints,
    Nodespaces,
    MappingAdopt,
    Attributes,
    MappingReference,
    MappingOrder,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class Node(object):
    """A node with original functionality from zodict.node.Node."""


@plumbing(
    MappingConstraints,
    Nodespaces,
    MappingAdopt,
    Attributes,
    MappingReference,
    MappingOrder,
    AsAttrAccess,
    DefaultInit,
    MappingNode,
    OdictStorage)
class AttributedNode(object):
    """A node with original functionality from zodict.node.AttributedNode."""

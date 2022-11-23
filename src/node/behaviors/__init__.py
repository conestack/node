from .adopt import MappingAdopt  # noqa
from .adopt import SequenceAdopt  # noqa
from .alias import Alias  # noqa
from .attributes import Attributes  # noqa
from .attributes import NodeAttributes  # noqa
from .cache import Cache  # noqa
from .cache import Invalidate  # noqa
from .cache import VolatileStorageInvalidate  # noqa
from .common import AsAttrAccess  # noqa
from .common import UnicodeAware  # noqa
from .common import UUIDAware  # noqa
from .constraints import MappingConstraints  # noqa
from .constraints import SequenceConstraints  # noqa
from .context import BoundContext  # noqa
from .events import EventAttribute  # noqa
from .events import Events  # noqa
from .events import suppress_events  # noqa
from .events import UnknownEvent  # noqa
from .factories import ChildFactory  # noqa
from .factories import FixedChildren  # noqa
from .factories import WildcardFactory  # noqa
from .fallback import Fallback  # noqa
from .filter import MappingFilter  # noqa
from .filter import SequenceFilter  # noqa
from .lifecycle import AttributesLifecycle  # noqa
from .lifecycle import Lifecycle  # noqa
from .lifecycle import suppress_lifecycle_events  # noqa
from .mapping import ClonableMapping  # noqa
from .mapping import EnumerableMapping  # noqa
from .mapping import ExtendedReadMapping  # noqa
from .mapping import ExtendedWriteMapping  # noqa
from .mapping import FullMapping  # noqa
from .mapping import ItemMapping  # noqa
from .mapping import IterableMapping  # noqa
from .mapping import Mapping  # noqa
from .mapping import MappingNode  # noqa
from .mapping import ReadMapping  # noqa
from .mapping import WriteMapping  # noqa
from .node import ContentishNode  # noqa
from .node import DefaultInit  # noqa
from .node import Node  # noqa
from .node import NodeInit  # noqa
from .nodespace import Nodespaces  # noqa
from .order import MappingOrder  # noqa
from .order import SequenceOrder  # noqa
from .reference import IndexViolationError  # noqa
from .reference import MappingReference  # noqa
from .reference import NodeIndex  # noqa
from .reference import NodeReference  # noqa
from .reference import SequenceReference  # noqa
from .schema import Schema  # noqa
from .schema import SchemaAsAttributes  # noqa
from .schema import SchemaAttributes  # noqa
from .schema import SchemaProperties  # noqa
from .sequence import MutableSequence  # noqa
from .sequence import Sequence  # noqa
from .sequence import SequenceNode  # noqa
from .storage import DictStorage  # noqa
from .storage import ListStorage  # noqa
from .storage import MappingStorage  # noqa
from .storage import OdictStorage  # noqa
from .storage import SequenceStorage  # noqa
from zope.deferredimport import deprecated


# B/C 2022-02-16 -> node.behaviors.Adopt
deprecated(
    '``Adopt`` has been renamed to ``MappingAdopt``. Please fix your import',
    Adopt='node.behaviors.adopt:MappingAdopt',
)
# B/C 2022-02-22 -> node.behaviors.NodeChildValidate
deprecated(
    '``NodeChildValidate`` has been renamed to ``MappingConstraints``. '
    'Please fix your import',
    NodeChildValidate='node.behaviors.constraints:MappingConstraints',
)
# B/C 2022-02-14 -> node.behaviors.Nodify
deprecated(
    '``Nodify`` has been renamed to ``MappingNode``. Please fix your import',
    Nodify='node.behaviors.mapping:MappingNode',
)
# B/C 2022-11-22 -> node.behaviors.Order
deprecated(
    '``Order`` has been renamed to ``MappingOrder``. Please fix your import',
    Order='node.behaviors.order:MappingOrder',
)
# B/C 2022-05-06 -> node.behaviors.Reference
deprecated(
    '``Reference`` has been renamed to ``MappingReference``. '
    'Please fix your import',
    Reference='node.behaviors.reference:MappingReference',
)
# B/C 2022-02-14 -> node.behaviors.Storage
deprecated(
    '``Storage`` has been renamed to ``MappingStorage``. Please fix your import',
    Storage='node.behaviors.storage:MappingStorage',
)

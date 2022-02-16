# -*- coding: utf-8 -*-
from .adopt import MappingAdopt  # noqa
from .alias import Alias  # noqa
from .attributes import Attributes  # noqa
from .attributes import NodeAttributes  # noqa
from .cache import Cache  # noqa
from .cache import Invalidate  # noqa
from .cache import VolatileStorageInvalidate  # noqa
from .common import AsAttrAccess  # noqa
from .common import ChildFactory  # noqa
from .common import FixedChildren  # noqa
from .common import GetattrChildren  # noqa
from .common import NodeChildValidate  # noqa
from .common import UnicodeAware  # noqa
from .common import UUIDAware  # noqa
from .context import BoundContext  # noqa
from .events import EventAttribute  # noqa
from .events import Events  # noqa
from .events import suppress_events  # noqa
from .events import UnknownEvent  # noqa
from .fallback import Fallback  # noqa
from .lifecycle import AttributesLifecycle  # noqa
from .lifecycle import Lifecycle  # noqa
from .mapping import ClonableMapping  # noqa
from .mapping import EnumerableMapping  # noqa
from .mapping import ExtendedReadMapping  # noqa
from .mapping import ExtendedWriteMapping  # noqa
from .mapping import FullMapping  # noqa
from .mapping import ItemMapping  # noqa
from .mapping import IterableMapping  # noqa
from .mapping import Mapping  # noqa
from .mapping import MappingNode  # noqa
from .mapping import Nodify  # noqa
from .mapping import ReadMapping  # noqa
from .mapping import WriteMapping  # noqa
from .node import DefaultInit  # noqa
from .node import Node  # noqa
from .nodespace import Nodespaces  # noqa
from .order import Order  # noqa
from .reference import NodeIndex  # noqa
from .reference import Reference  # noqa
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
# B/C 2022-02-14 -> node.behaviors.MappingStorage
deprecated(
    '``Storage`` has been renamed to ``MappingStorage``. Please fix your import',
    Storage='node.behaviors.storage:MappingStorage',
)

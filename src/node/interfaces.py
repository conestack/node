from zope.deferredimport import deprecated
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.common.collections import IMutableSequence
from zope.interface.common.mapping import IFullMapping
from zope.lifecycleevent import IObjectAddedEvent
from zope.lifecycleevent import IObjectCreatedEvent
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


try:
    from zope.location.interfaces import ILocation
except ImportError as e:
    class ILocation(Interface):
        """Objects that can be located in a hierachy.

        This is a replacement for ``zope[.app].interface.ILocation``, as
        zope[.app].interface cannot be easily used on App Engine due to its
        dependency on ``zope.proxy``, which has C extensions that are not
        implemented in Python.

        This implementation is slightly simpler than the original one, as
        this is only intended to be used on App Engine, where the original
        interface is not available anyway, so nobody should register
        any adapters/utilities for it.
        """

        __parent__ = Attribute('The parent in the location hierarchy.')
        __name__ = Attribute('The name within the parent')


###############################################################################
# events
###############################################################################

class INodeCreatedEvent(IObjectCreatedEvent):
    """An new Node was born."""


class INodeAddedEvent(IObjectAddedEvent):
    """An Node has been added to its parent."""


class INodeModifiedEvent(IObjectModifiedEvent):
    """An Node has been modified."""


class INodeRemovedEvent(IObjectRemovedEvent):
    """An Node has been removed from its parent."""


class INodeDetachedEvent(IObjectRemovedEvent):
    """An Node has been detached from its parent."""


###############################################################################
# helpers
###############################################################################

class IAttributeAccess(Interface):
    """Provides Attribute access to dict like context.

    Dome dict API functions are wrapped.
    """

    def __getattr__(name):
        """Call ``__getitem__`` on context."""

    def __setattr__(name, value):
        """Call ``__setattr__`` on context."""

    def __getitem__(name):
        """Call ``__getitem__`` on context."""

    def __setitem__(name, value):
        """Call ``__setitem__`` on context."""

    def __delitem__(name):
        """Call ``__delitem__`` on context."""


class IAliaser(Interface):
    """Generic Aliasing Interface."""

    def alias(key):
        """Return alias for key."""

    def unalias(aliased_key):
        """Return the key belonging to aliased_key."""


###############################################################################
# markers
###############################################################################

class IRoot(Interface):
    """Marker for a root node."""


class ILeaf(Interface):
    """Marker for node without children."""


class IOrdered(Interface):
    """Marker for nodes containing ordered children."""


class ICallable(Interface):
    """Provide a ``__call__`` function."""

    def __call__():
        """Expose the tree contents to an output channel."""


###############################################################################
# node
###############################################################################

class INode(ILocation):
    """Basic node interface."""

    name = Attribute('Read only property mapping ``__name__``.')
    parent = Attribute('Read only property mapping ``__parent__``.')
    path = Attribute('Path of node as list')
    root = Attribute(
        'Root node. Normally wither the node with no more parent or a node '
        'implementing ``node.interfaces.IRoot``'
    )

    def detach(name):
        """Detach child Node."""

    def acquire(interface):
        """Traverse parents until interface provided. Return first parent
        providing interface or None if no parent matches.
        """

    def printtree():
        """Debugging helper."""


###############################################################################
# plumbing behaviors
###############################################################################

class IDefaultInit(Interface):
    """Plumbing behavior providing default ``__init__`` function on node."""

    def __init__(name=None, parent=None):
        """Set ``self.__name__`` and ``self.__parent__`` at init time."""


class IMappingNode(INode, IFullMapping):
    """Plumbing behavior to Fill in gaps for full mapping node API.

    Plumbing hooks:

    * ``copy``
        set ``__name__`` and ``__parent__`` attributes on new copy.
    """

    def filtereditervalues(interface):
        """Yield filtered child nodes by interface."""

    def filteredvalues(interface):
        """Return filtered child nodes by interface."""


# B/C 2022-02-14 -> node.interfaces.INodify
deprecated(
    '``INodify`` has been renamed to ``IMappingNode``. Please fix your import',
    INodify='node.interfaces:IMappingNode',
)


class ISequenceNode(INode, IMutableSequence):
    """Plumbing behavior to Fill in gaps for full sequence node API.

    Plumbing hooks:

    * ``__getitem__``
        Cast index to int if index is no slice.

    * ``__setitem__``
        Prevents setting slice values. Cast index to int.

    * ``__delitem__``
        Cast index to int if index is no slice. Update indices on remaining
        contained children.

    * ``insert``
        Cast index to int. Update indices contained children.

    * ``detach``
        Update indices contained children.
    """

    def __index__():
        """The index of this node if contained in another sequence. If node not
        contained in a sequence node, an ``IndexError`` is raised.
        """


class IMappingAdopt(Interface):
    """Plumbing behavior that provides ``__name__`` and ``__parent__``
    attribute adoption on child nodes of mapping.

    Plumbing hooks:

    * ``__setitem__``
        Sets ``__name__`` and ``__parent__`` attributes of child node.
        Revert change if error occurs in pipeline.

    * ``setdefault``
        Re-route ``__getitem__`` and ``__setitem__``, skipping ``next_``.
    """


# B/C 2022-02-16 -> node.interfaces.IAdopt
deprecated(
    '``IAdopt`` has been renamed to ``IMappingAdopt``. Please fix your import',
    IAdopt='node.interfaces:IMappingAdopt',
)


class ISequenceAdopt(Interface):
    """Plumbing behavior that provides ``__name__`` and ``__parent__``
    attribute adoption on child nodes of sequence.

    Plumbing hooks:

    * ``__setitem__``
        Sets ``__name__`` and ``__parent__`` attributes of child node.
        Revert change if error occurs in pipeline.

    * ``insert``
        Sets ``__name__`` and ``__parent__`` attributes of child node.
        Revert change if error occurs in pipeline.
    """


class IConstraints(Interface):
    """Base interface for defining node constraints.
    """

    child_constraints = Attribute(
        'Sequence of types or interfaces of allowed node children '
        'or None if no constraints'
    )


class IMappingConstraints(IConstraints):
    """Plumbing behavior for constraints on mapping nodes.

    Plumbing hooks:

    * ``__setitem__``
        Check if given value is instance of type or implements interface
        defined in ``child_constraints``. Raise ``ValuError`` on mismatch.
    """


# B/C 2022-02-22 -> node.interfaces.INodeChildValidate
deprecated(
    '``INodeChildValidate`` has been renamed to ``IMappingConstraints``. '
    'Please fix your import',
    INodeChildValidate='node.interfaces:IMappingConstraints',
)


class ISequenceConstraints(IConstraints):
    """Plumbing behavior for constraints on mapping nodes.

    Plumbing hooks:

    * ``__setitem__``
        Check if given value is instance of type or implements interface
        defined in ``child_constraints``. Raise ``ValuError`` on mismatch.

    * ``insert``
        Check if given value is instance of type or implements interface
        defined in ``child_constraints``. Raise ``ValuError`` on mismatch.
    """


class IUnicodeAware(Interface):
    """Plumbing behavior to ensure unicode for keys and string values.

    Plumbing hooks:

    * ``__getitem__``
        Ensure unicode key.

    * ``__setitem__``
        Ensure unicode key and unicode value if value is basestring.

    * ``__delitem__``
        Ensure unicode key
    """


class IAlias(Interface):
    """Plumbing behavior that provides aliasing of child keys.

    Plumbing hooks:

    * ``__init__``
        Takes care of 'aliaser' keyword argument and set to ``self.aliaser``
        if given.

    * ``__getitem__``
        Return child by aliased key.

    * ``__setitem__``
        Set child by aliased key.

    * ``__delitem__``
        Delete item by aliased key.

    * ``__iter__``
        Iterate aliased keys.
    """

    aliaser = Attribute('``IAliaser`` implementation.')


class IAsAttrAccess(Interface):
    """Plumbing behavior to get node as IAttributeAccess implementation."""

    def as_attribute_access():
        """Return this node as IAttributeAccess implementing object."""


class IChildFactory(Interface):
    """Plumbing behavior providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    """

    factories = Attribute('Dict like object containing key/factory pairs.')

    def __iter__():
        """Return iterator of factory keys."""


class IFixedChildren(Interface):
    """Plumbing behavior that initializes a fixed dictionary as children.

    The children are instantiated during ``__init__`` and adopted by the
    class using this behavior. They cannot receive init arguments, but
    could retrieve configuration from their parent.

    Plumbing hooks:

    * ``__init__``
        Create fixed children defined in ``fixed_children_factories``
    """

    fixed_children_factories = Attribute(
        'Dict like object containing child factories.'
    )

    def __delitem__(key):
        """Deny deleting, read-only."""

    def __setitem__(key, val):
        """Deny setting item, read-only."""


class INodespaces(Interface):
    """Plumbing behavior for providing nodespaces on node.

    A nodespace is a seperate node with special keys - pre- and postfixed with
    ``__`` and gets mapped on storage write operations.

    Plumbing hooks:

    * ``__getitem__``
        Return nodespace if key pre- and postfixed with '__', otherwise child
        from ``__children__`` nodespace.

    * ``__setitem__``
        Set nodespace if key pre- and postfixed with '__', otherwise set child
        to ``__children__`` nodespace.

    * ``__delitem__``
        Delete nodespace if key pre- and postfixed with '__', otherwise delete
        child from ``__children__`` nodespace.
    """

    nodespaces = Attribute('Nodespaces. Dict like object.')


class INodeAttributes(Interface):
    """Marker interface for node attributes."""


class IAttributes(Interface):
    """Plumbing behavior to provide attributes on node."""

    attrs = Attribute('``INodeAttributes`` implementation.')
    attrs_factory = Attribute('``INodeAttributes`` implementation class.')
    attribute_access_for_attrs = Attribute(
        'Return ``attrs`` wrapped by ``node.utils.AttributeAccess``'
    )


class ILifecycle(Interface):
    """Plumbing behavior taking care of lifecycle events.

    Plumbing hooks:

    * ``__init__``
        Trigger created event.

    * ``__setitem__``
        Trigger added event.

    * ``__delitem__``
        Trigger removed event.

    * ``detach``
        Trigger detached event.
    """

    events = Attribute(
        'Dict with lifecycle event classes to use for notification.'
    )


class IAttributesLifecycle(Interface):
    """Plumbing behavior for handling lifecycle events on attribute
    manipulation.

    Plumbing hooks:

    * ``__setitem__``
        Trigger modified event.

    * ``__delitem__``
        Trigger modified event.
    """


class IInvalidate(Interface):
    """Plumbing behavior for node invalidation."""

    def invalidate(key=None):
        """Invalidate child with key or all children of this node.

        Raise KeyError if child does not exist for key if given.
        """


class ICache(Interface):
    """Plumbing behavior for caching.

    Plumbing hooks:

    * ``__getitem__``
        Return cached child or read child.

    * ``__setitem__``
        Remove child from cache and set item.

    * ``__delitem__``
        Remove child from cache.

    * ``__iter__``
        Iterate cached keys or iterate.

    * ``invalidate``
        Invalidate cache.
    """

    cache = Attribute('Dict like object representing the cache.')


class IOrder(Interface):
    """Plumbing behavior for ordering support."""

    first_key = Attribute(
        'First child key. ``KeyError`` is raised if node has no children.'
    )
    last_key = Attribute(
        'Last child key. ``KeyError`` is raised if node has no children.'
    )

    def next_key(key):
        """Return key after given key. Raise ``KeyError`` if key corresponds
        to last item in node.
        """

    def prev_key(key):
        """Return key before given key. Raise ``KeyError`` if key corresponds
        to first item in node.
        """

    def swap(node_a, node_b):
        """Swap 2 nodes."""

    def insertfirst(newnode):
        """Insert newnode as first node."""

    def insertlast(newnode):
        """Insert newnode as last node."""

    def insertbefore(newnode, refnode):
        """Insert newnode before refnode.

        ``__name__`` on newnode must be set.

        This function only supports adding of new nodes before the given
        refnode. If you want to move nodes you have to detach them from the
        tree first.
        """

    def insertafter(newnode, refnode):
        """Insert newnode after refnode.

        ``__name__`` on newnode must be set.

        This function only supports adding of new nodes after the given
        refnode. If you want to move nodes you have to detach them from the
        tree first.
        """


class IUUID(Interface):
    """Plumbing behavior for providing a uuid on a node."""

    uuid = Attribute('``uuid.UUID`` of this node.')


class IUUIDAware(IUUID):
    """Be aware of node uuid for several operations.

    Plumbing hooks:

    * ``__init__``
        Create and set uuid.

    * ``copy``
        Set new uuid on copied obejct. Considers
        ``overwrite_recursiv_on_copy``.
    """

    overwrite_recursiv_on_copy = Attribute(
        'Flag whether to set new UUID on children as well when calling '
        '``node.copy()``. This only makes sence for nodes performing a '
        '``deepcopy`` or anythin equivalent also creating copies '
        'of it\'s children.'
    )
    uuid_factory = Attribute('Factory function creating new uuid instances')

    def set_uuid_for(node, override=False, recursiv=False):
        """Set ``uuid`` for node. If ``override`` is True, override existing
        ``uuid`` attributes, if ``recursiv`` is True, set new ``uuid`` on
        children as well.
        """


class IReference(IUUID):
    """Plumbing behavior holding an index of all nodes contained in the tree.

    Plumbing hooks:

    * ``__init__``
        Create and set uuid.

    * ``__setitem__``
        Set child in index.

    * ``__delitem__``
        Delete child from index.

    * ``detach``
        Reduce index of detached child.
    """

    index = Attribute('The tree node index')

    def node(uuid):
        """Return node by uuid located anywhere in this nodetree."""


class IMappingStorage(Interface):
    """Plumbing behavior providing mapping storage related endpoints.

    Minimum Storage requirement is described below. An implementation of this
    interface could provide other storage related methods as appropriate.
    """

    def __getitem__(key):
        """Return item from Storage."""

    def __setitem__(key, val):
        """Set item to storage."""

    def __delitem__(key):
        """Delete Item from storage."""

    def __iter__():
        """Iter throught storage keys."""


# B/C 2022-02-14 -> node.interfaces.IStorage
deprecated(
    '``IStorage`` has been renamed to ``IMappingStorage``. Please fix your import',
    IStorage='node.interfaces:IMappingStorage',
)


class ISequenceStorage(Interface):
    """Plumbing behavior providing sequence storage related endpoints.

    Minimum Storage requirement is described below. An implementation of this
    interface could provide other storage related methods as appropriate.
    """

    def __len__():
        """Return length of storage."""

    def __getitem__(index):
        """Return item from Storage."""

    def __setitem__(index, value):
        """Set item to storage."""

    def __delitem__(index):
        """Delete Item from storage."""

    def insert(index, value):
        """Insert item to storage."""


class IFallback(Interface):
    """Plumbing behavior providing a way to fall back to values by subpath
    stored on sibling or parent nodes.

    If a key is not found, a lookup on parent is made if ``fallback_key`` is
    defined. If so, it looks in the subtree defined by ``fallback_key`` if the
    key is available there using the same subpath. If nothing is found by given
    subpath in fallback subtree, it traverses rootwards repeating the procedure
    until desired value is found.
    """

    fallback_key = Attribute(
        'Key to be used as fallback if an item was not found.'
    )

    def __getitem__(key):
        """Lookup fallback if item is not available on node."""


class IEvents(Interface):
    """Plumbing behavior providing event dispatching."""

    def register_event(event):
        """Register event type.

        :param event: Event name as string.
        """

    def bind(**kw):
        """Bind subscribers to events.

        :param kw: Each keyword argument is the event name and the argument
            value is the subscriber callable.
        """

    def unbind(event=None, subscriber=None):
        """Unbind subscribers.

        :param event: Event name. If not given, all events are affected.
        :param subscriber: Subscriber callable. If not given, all subscribers
            are affected.
        """

    def dispatch(event, *args, **kw):
        """Dispatch event.

        :param event: Event name.
        :param args: Arguments passed to subscribers.
        :patam kw: Keyword arguments passed to subscribers.
        """


class ISchema(Interface):
    """Plumbing behavior providing schema validation and value serialization
    on node values.

    Plumbing hooks:

    * ``__getitem__``
        Check if ``name`` contained in schema. If not, return value as is. If
        schema field is found, return deserialized value. If no value for key
        yet, return default from schema field if defined.

    * ``__setitem__``
        Check if ``name`` contained in schema. If not, set value as is. If
        schema field defined, validate given value. If validation succeeds,
        write serialized value.
    """

    schema = Attribute(
        'Dict of child names as keys and ``node.schema.Field`` '
        'or deriving instances as values.'
    )


class ISchemaAsAttributes(IAttributes):
    """Plumbing behavior providing schema validation and value serialization
    on node values. The difference to ``ISchema`` interface is that the schema
    fields are accessed via ``attrs`` instead of direct container access. This
    way it's possible to distinguish between data which bolongs to the node
    itself and children of the node while both are contained in the same
    storage.

    Plumbing hooks:

    * ``__getitem__``
        Raises ``KeyError`` if name contained in schema. Schema attributes are
        supposed to be accessed via ``attrs``.

    * ``__setitem__``
        Raises ``KeyError`` if name contained in schema. Schema attributes are
        supposed to be accessed via ``attrs``.

    * ``__delitem__``
        Raises ``KeyError`` if name contained in schema. Schema attributes are
        supposed to be accessed via ``attrs``.

    * ``__iter__``
        Iterates downstream ``__iter__`` and ignores all names contained in
        schema.
    """

    schema = Attribute(
        'Dict of child names as keys and ``node.schema.Field`` '
        'or deriving instances as values.'
    )


class ISchemaProperties(Interface):
    """Plumbing behavior for providing schema fields as class properties.

    For all ``node.schema.Field`` instances found on class
    ``node.behaviors.schema.SchemaProperty`` descriptors are created handling
    the field values.

    Plumbing hooks:

    * ``__getitem__``
        Raises ``KeyError`` if name used as schema property. Schema property
        are supposed to be accessed via ``__getattribute__``.

    * ``__setitem__``
        Raises ``KeyError`` if name used as schema property. Schema property
        are supposed to be accessed via ``__getattribute__``.

    * ``__delitem__``
        Raises ``KeyError`` if name used as schema property. Schema property
        are supposed to be accessed via ``__getattribute__``.

    * ``__iter__``
        Iterates downstream ``__iter__`` and ignores all names used as schema
        properties.
    """


class IBoundContext(Interface):
    """Plumbing behavior for scoping objects to interfaces and classes.
    """

    def bind_context(context):
        """Bind this object to context interfaces and or classes.

        :param event: Either single interface or class or list/tuple of
            interfaces and/or classes.
        """

    def context_matches(obj):
        """Check whether given object matches bound context scope."""

# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface
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
    """An new Node was born.
    """


class INodeAddedEvent(IObjectAddedEvent):
    """An Node has been added to its parent.
    """


class INodeModifiedEvent(IObjectModifiedEvent):
    """An Node has been modified.
    """


class INodeRemovedEvent(IObjectRemovedEvent):
    """An Node has been removed from its parent.
    """


class INodeDetachedEvent(IObjectRemovedEvent):
    """An Node has been detached from its parent.
    """


###############################################################################
# helpers
###############################################################################


class IAttributeAccess(Interface):
    """Provides Attribute access to dict like context.

    Dome dict API functions are wrapped.
    """
    def __getattr__(name):
        """Call __getitem__ on context.
        """

    def __setattr__(name, value):
        """Call __setattr__ on context.
        """

    def __getitem__(name):
        """Call __getitem__ on context.
        """

    def __setitem__(name, value):
        """Call __setitem__ on context.
        """

    def __delitem__(name):
        """Call __delitem__ on context.
        """


class IAliaser(Interface):
    """Generic Aliasing Interface.
    """
    def alias(key):
        """Return alias for key.
        """

    def unalias(aliased_key):
        """Return the key belonging to aliased_key.
        """


###############################################################################
# markers
###############################################################################


class IRoot(Interface):
    """Marker for a root node.
    """


class ILeaf(Interface):
    """Marker for node without children.
    """


class IOrdered(Interface):
    """Marker for nodes containing ordered children.
    """


class ICallable(Interface):
    """Provide a ``__call__`` function.
    """

    def __call__():
        """Expose the tree contents to an output channel.
        """


###############################################################################
# node
###############################################################################


class INode(ILocation, IFullMapping):
    """Basic node interface.
    """
    name = Attribute('Read only property mapping ``__name__``.')
    parent = Attribute('Read only property mapping ``__parent__``.')
    path = Attribute('Path of node as list')
    root = Attribute(
        'Root node. Normally wither the node with no more parent or a node '
        'implementing ``node.interfaces.IRoot``')

    def detach(key):
        """Detach child Node.
        """

    def acquire(interface):
        """Traverse parents until interface provided. Return first parent
        providing interface or None if no parent matches.
        """

    def filtereditervalues(interface):
        """Yield filtered child nodes by interface.
        """

    def filteredvalues(interface):
        """Return filtered child nodes by interface.
        """

    def printtree():
        """Debugging helper.
        """


###############################################################################
# plumbing behaviors
###############################################################################


class IDefaultInit(Interface):
    """Plumbing behavior providing default ``__init__`` function on node.
    """
    def __init__(name=None, parent=None):
        """Set ``self.__name__`` and ``self.__parent__`` at init time.
        """


class INodify(INode):
    """Plumbing behavior to Fill in gaps for full INode API.

    Plumbing hooks:

    copy
        set ``__name__`` and ``__parent__`` attributes on new copy.
    """


class IAdopt(Interface):
    """Plumbing behavior that provides adoption of children.

    Plumbing hooks:

    __setitem__
        Takes care of ``__name__`` and ``__parent__`` attributes of child node.

    setdefault
        Re-route ``__getitem__`` and ``__setitem__``, skipping ``_next``.
    """


class INodeChildValidate(Interface):
    """Plumbing behavior for child node validation.

    Plumbing hooks:

    __setitem__
        If ``allow_non_node_childs`` is False, check if given child is instance
        of node, otherwise raise ``ValuError``.
    """
    allow_non_node_childs = Attribute(
        'Flag wether this node may contain non node based children.')


class IUnicodeAware(Interface):
    """Plumbing behavior to ensure unicode for keys and string values.

    Plumbing hooks:

    __getitem__
        Ensure unicode key.

    __setitem__
        Ensure unicode key and unicode value if value is basestring.

    __delitem__
        Ensure unicode key
    """


class IAlias(Interface):
    """Plumbing behavior that provides aliasing of child keys.

    Plumbing hooks:

    __init__
        Takes care of 'aliaser' keyword argument and set to ``self.aliaser``
        if given.

    __getitem__
        Return child by aliased key.

    __setitem__
        Set child by aliased key.

    __delitem__
        Delete item by aliased key.

    __iter__
        Iterate aliased keys.
    """
    aliaser = Attribute('``IAliaser`` implementation.')


class IAsAttrAccess(Interface):
    """Plumbing behavior to get node as IAttributeAccess implementation.
    """
    def as_attribute_access():
        """Return this node as IAttributeAccess implementing object.
        """


class IChildFactory(Interface):
    """Plumbing behavior providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    """
    factories = Attribute('Dict like object containing key/factory pairs.')

    def __iter__():
        """Return iterator of factory keys.
        """


class IFixedChildren(Interface):
    """Plumbing behavior that initializes a fixed dictionary as children.

    The children are instantiated during ``__init__`` and adopted by the
    class using this behavior. They cannot receive init arguments, but
    could retrieve configuration from their parent.

    Plumbing hooks:

    __init__
        Create fixed children defined in ``fixed_children_factories``
    """
    fixed_children_factories = Attribute(
        'Dict like object containing child factories.')

    def __delitem__(key):
        """Deny deleting, read-only.
        """

    def __setitem__(key, val):
        """Deny setting item, read-only.
        """


class IGetattrChildren(Interface):
    """Plumbing behavior for child access via ``__getattr__``, given the
    attribute name is unused.
    """
    def __getattr__(name):
        """Map ``__getitem__``.
        """


class INodespaces(Interface):
    """Plumbing behavior for providing nodespaces on node.

    A nodespace is a seperate node with special keys - pre- and postfixed with
    ``__`` and gets mapped on storage write operations.

    Plumbing hooks:

    __getitem__
        Return nodespace if key pre- and postfixed with '__', otherwise child
        from ``__children__`` nodespace.

    __setitem__
        Set nodespace if key pre- and postfixed with '__', otherwise set child
        to ``__children__`` nodespace.

    __delitem__
        Delete nodespace if key pre- and postfixed with '__', otherwise delete
        child from ``__children__`` nodespace.
    """
    nodespaces = Attribute('Nodespaces. Dict like object.')


class IAttributes(Interface):
    """Plumbing behavior to provide attributes on node.
    """
    attrs = Attribute('``INodeAttributes`` implementation.')
    attrs_factory = Attribute('``INodeAttributes`` implementation class.')


class ILifecycle(Interface):
    """Plumbing behavior taking care of lifecycle events.

    Plumbing hooks:

    __init__
        Trigger created event.

    __setitem__
        Trigger added event.

    __delitem__
        Trigger removed event.

    detach
        Trigger detached event.
    """
    events = Attribute(
        'Dict with lifecycle event classes to use for notification.')


class IAttributesLifecycle(Interface):
    """Plumbing behavior for handling ifecycle events at attributes
    manipulation.

    Plumbing hooks:

    __setitem__
        Trigger modified event.

    __delitem__
        Trigger modified event.
    """


class IInvalidate(Interface):
    """Plumbing behavior for node invalidation.
    """
    def invalidate(key=None):
        """Invalidate child with key or all children of this node.

        Raise KeyError if child does not exist for key if given.
        """


class ICache(Interface):
    """Plumbing behavior for caching.

    Plumbing hooks:

    __getitem__
        Return cached child or read child.

    __setitem__
        Remove child from cache and set item.

    __delitem__
        Remove child from cache.

    __iter__
        Iterate cached keys or iterate.

    invalidate
        Invalidate cache.
    """
    cache = Attribute('Dict like object representing the cache.')


class IOrder(Interface):
    """Plumbing behavior for ordering support.
    """

    def swap(node_a, node_b):
        """Swap 2 nodes.
        """

    def insertfirst(newnode):
        """Insert newnode as first node.
        """

    def insertlast(newnode):
        """Insert newnode as last node.
        """

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
    """Plumbing behavior for providing a uuid on a node.
    """
    uuid = Attribute('``uuid.UUID`` of this node.')


class IUUIDAware(IUUID):
    """Be aware of node uuid for several operations.

    Plumbing hooks:

    __init__
        Create and set uuid.

    copy
        Set new uuid on copied obejct. Considers
        ``overwrite_recursiv_on_copy``.
    """
    overwrite_recursiv_on_copy = Attribute(
        'Flag whether to set new UUID on children as well when calling '
        '``node.copy()``. This only makes sence for nodes performing a '
        '``deepcopy`` or anythin equivalent also creating copies '
        'of it\'s children.')

    uuid_factory = Attribute('Factory function creating new uuid instances')

    def set_uuid_for(node, override=False, recursiv=False):
        """Set ``uuid`` for node. If ``override`` is True, override existing
        ``uuid`` attributes, if ``recursiv`` is True, set new ``uuid`` on
        children as well.
        """


class IReference(IUUID):
    """Plumbing behavior holding an index of all nodes contained in the tree.

    Plumbing hooks:

    __init__
        Create and set uuid.

    __setitem__
        Set child in index.

    __delitem__
        Delete child from index.

    detach
        Reduce index of detached child.
    """
    index = Attribute('The tree node index')

    def node(uuid):
        """Return node by uuid located anywhere in this nodetree.
        """


class IStorage(Interface):
    """Plumbing behavior providing storage related endpoints.

    Minimum Storage requirement is described below. An implementation of this
    interface could provide other storage related methods as appropriate.
    """

    def __getitem__(key):
        """Return Item from Storage.
        """

    def __setitem__(key, val):
        """Set item to storage.
        """

    def __delitem__(key):
        """Delete Item from storage.
        """

    def __iter__():
        """Iter throught storage keys.
        """


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
        'Key to be used as fallback if an item was not found.')

    def __getitem__(key):
        """Lookup fallback if item is not available on node.
        """


class IEvents(Interface):
    """Plumbing behavior providing event dispatching.
    """

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

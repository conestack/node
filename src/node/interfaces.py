from zope.interface import (
    Interface,
    Attribute,
)
from zope.interface.common.mapping import (
    IEnumerableMapping,
    IWriteMapping,
    IFullMapping,
)
try:
    from zope.location.interfaces import ILocation
except ImportError, e:
    try:
        from zope.app.location.interfaces import ILocation # BBB
    except ImportError, e:
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

try:
    from zope.lifecycleevent import (
        IObjectCreatedEvent,
        IObjectAddedEvent,
        IObjectModifiedEvent,
        IObjectRemovedEvent,
    )
except ImportError, e:                                      #pragma NO COVERAGE
    # BBB, XXX: remove this soon, relict from ``zodict``
    from zope.app.event.interfaces import IObjectEvent      #pragma NO COVERAGE
    class IObjectCreatedEvent(IObjectEvent): pass           #pragma NO COVERAGE
    class IObjectAddedEvent(IObjectEvent): pass             #pragma NO COVERAGE
    class IObjectModifiedEvent(IObjectEvent): pass          #pragma NO COVERAGE
    class IObjectRemovedEvent(IObjectEvent): pass           #pragma NO COVERAGE


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
    name = Attribute(u"Read only property mapping ``__name__``.")
    parent = Attribute(u"Read only property mapping ``__parent__``.")
    path = Attribute(u"Path of node as list")
    root = Attribute(u"Root node. Normally wither the node with no more "
                     u"parent or a node implementing ``node.interfaces.IRoot``")
    
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
# plumbing parts
###############################################################################


class IDefaultInit(Interface):
    """Plumbing part providing default ``__init__`` function on node.
    """
    def __init__(name=None, parent=None):
        """Set ``self.__name__`` and ``self.__parent__`` at init time.
        """


class INodify(INode):
    """Plumbing part to Fill in gaps for full INode API.
    
    Plumbing hooks:
    
    copy
        set ``__name__`` and ``__parent__`` attributes on new copy.
    """


class IAdopt(Interface):
    """Plumbing part that provides adoption of children.
    
    Plumbing hooks:
    
    __setitem__
        Takes care of ``__name__`` and ``__parent__`` attributes of child node.
      
    setdefault
        Re-route ``__getitem__`` and ``__setitem__``, skipping ``_next``.
    """


class INodeChildValidate(Interface):
    """Plumbing part for child node validation.
    
    Plumbing hooks:
    
    __setitem__
        If ``allow_non_node_childs`` is False, check if given child is instance
        of node, otherwise raise ``ValuError``.
    """
    allow_non_node_childs = Attribute(u"Flag wether this node may contain non "
                                      u"node based children.")


class IUnicodeAware(Interface):
    """Plumbing part to ensure unicode for keys and string values.
    
    Plumbing hooks:
    
    __getitem__
        Ensure unicode key.
    
    __setitem__
        Ensure unicode key and unicode value if value is basestring.
    
    __delitem__
        Ensure unicode key
    """


class IAlias(Interface):
    """Plumbing part that provides aliasing of child keys.
    
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
    aliaser = Attribute(u"``IAliaser`` implementation.")


class IAsAttrAccess(Interface):
    """Plumbing part to get node as IAttributeAccess implementation.
    """
    def as_attribute_access():
        """Return this node as IAttributeAccess implementing object.
        """


class IChildFactory(Interface):
    """Plumbing part providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    """
    factories = Attribute(u"Dict like object containing key/factory pairs.")
    
    def __iter__():
        """Return iterator of factory keys. 
        """


class IFixedChildren(Interface):
    """Plumbing part that initializes a fixed dictionary as children.

    The children are instantiated during ``__init__`` and adopted by the
    class using this part. They cannot receive init arguments, but
    could retrieve configuration from their parent.
    
    Plumbing hooks:
    
    __init__
        Create fixed children defined in ``fixed_children_factories``
    """
    fixed_children_factories = Attribute(u"Dict like object containing child "
                                         u"factories.")
    
    def __delitem__(key):
        """Deny deleting, read-only.
        """

    def __setitem__(key, val):
        """Deny setting item, read-only.
        """


class IGetattrChildren(Interface):
    """Plumbing part for child access via ``__getattr__``, given the attribute
    name is unused.
    """
    def __getattr__(name):
        """Map ``__getitem__``.
        """


class INodespaces(Interface):
    """Plumbing part for providing nodespaces on node.
    
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
    nodespaces = Attribute(u"Nodespaces. Dict like object.")


class IAttributes(Interface):
    """Plumbing part to provide attributes on node.
    """
    attrs = Attribute(u"``INodeAttributes`` implementation.")
    attrs_factory = Attribute(u"``INodeAttributes`` implementation class")


class ILifecycle(Interface):
    """Plumbing part taking care of lifecycle events.
    
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
    events = Attribute(u"Dict with lifecycle event classes to use for "
                       u"notification.")


class IAttributesLifecycle(Interface):
    """Plumbing part for handling ifecycle events at attributes manipulation.
    
    Plumbing hooks:
    
    __setitem__
        Trigger modified event.
    
    __delitem__
        Trigger modified event.
    """


class IInvalidate(Interface):
    """Plumbing part for node invalidation.
    """
    def invalidate(key=None):
        """Invalidate child with key or all children of this node.
        """


class ICache(Interface):
    """Plumbing part for caching.
    
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
    cache = Attribute(u"Dict like object representing the cache.")


class IOrder(Interface):
    """Plumbing part for ordering support.
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
    """Plumbing part for providing a uuid on a node.
    """
    uuid = Attribute(u"``uuid.UUID`` of this node.")


class IUUIDAware(IUUID):
    """Be aware of node uuid for several operations.
    
    Plumbing hooks:
    
    __init__
        Create and set uuid.
    
    copy
        Set new uuid on copied obejct. Considers ``overwrite_recursiv_on_copy``. 
    """
    overwrite_recursiv_on_copy = Attribute(u"Flag whether to set new UUID on "
                                           u"children as well when calling "
                                           u"``node.copy()``. This only makes "
                                           u"sence for nodes performing a "
                                           u"``deepcopy`` or anythin "
                                           u"equivalent also creating copies "
                                           u"of it's children.")
    
    def set_uuid_for(node, override=False, recursiv=False):
        """Set ``uuid`` for node. If ``override`` is True, override existing
        ``uuid`` attributes, if ``recursiv`` is True, set new ``uuid`` on
        children as well.
        """


class IReference(IUUID):
    """Plumbing part holding an index of all nodes contained in the tree.
    
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
    index = Attribute(u"The tree node index")
    
    def node(uuid):
        """Return node by uuid located anywhere in this nodetree.
        """


class IStorage(Interface):
    """Plumbing part providing storage related endpoints.
    
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


#class IWrap(Interface):
#    """
#    """


###############################################################################
# BBB Will be removed by node 1.0
###############################################################################


class INodeAttributes(IEnumerableMapping, IWriteMapping):
    """Interface describing the attributes of a (lifecycle) Node.

    Promise to throw modification related events when calling IWriteMapping
    related functions.

    You do not instanciate this kind of object directly. This is done due to
    ``LifecycleNode.attributes`` access. You can provide your own
    ``INodeAttributes`` implementation by setting
    ``LifecycleNode.attributes_factory``.
    """
    changed = Attribute(u"Flag indicating if attributes were changed or not.")

    def __init__(node):
        """Initialize object.

        Takes attributes refering node at creation time.
        """


class ICallableNode(INode):
    """Node which implements the ``__call__`` function.
    """

    def __call__():
        """Expose the tree contents to an output channel.
        """


class IAttributedNode(INode):
    """Node which care about its attributes.
    """
    attributes = Attribute(u"``INodeAttributes`` implementation.")
    attributes_factory = Attribute(u"``INodeAttributes`` implementation class")


class ILifecycleNode(INode):
    """Node which care about its lifecycle.
    """
    events = Attribute(u"Dict with lifecycle event classes to use for "
                       u"notification.")


class IComposition(INode):
    pass
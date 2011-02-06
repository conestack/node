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
except ImportError, e: # BBB
    from zope.app.event.interfaces import IObjectEvent
    class IObjectCreatedEvent(IObjectEvent):
        pass
    class IObjectAddedEvent(IObjectEvent):
        pass
    class IObjectModifiedEvent(IObjectEvent):
        pass
    class IObjectRemovedEvent(IObjectEvent):
        pass


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
    
    Implementation is supposed to be an adapter like object.
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
        """returns the alias for a key
        """

    def unalias(aliased_key):
        """returns the key belonging to an aliased_key
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


###############################################################################
# node
###############################################################################


class INode(ILocation, IFullMapping):
    """A node.
    """
    path = Attribute(u"Path of node as list")
    root = Attribute(u"Root node. Normally wither the node with no more "
                     u"parent or a node implementing ``node.interfaces.IRoot``")
    
    def detach(key):
        """Detach child Node.
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


class IAdopt(Interface):
    """XXX: Description of plumbs
    """


class IAlias(Interface):
    """XXX: Desctiption of plumbs
    """


class IAsAttrAccess(Interface):
    """Part to get node as IAttributeAccess implementation.
    """

    def as_attribute_access():
        """Return this node as IAttributeAccess implementing object.
        """


class IAttributes(Interface):
    """Provide attributes on node.
    """
    attrs = Attribute(u"``INodeAttributes`` implementation.")
    attrs_factory = Attribute(u"``INodeAttributes`` implementation class")


class IAttributesLifecycle(Interface):
    """XXX: Description of plumbs
    """


class ICache(Interface):
    """Cache nodes.
    """


class ICallable(Interface):
    """Provide a ``__call__`` function.
    """

    def __call__():
        """Expose the tree contents to an output channel.
        """


class IInvalidate(Interface):
    """Node invalidation.
    """

    def invalidate(key=None):
        """Invalidate child with key or all childs of this node.
        """


class ILifecycle(Interface):
    """Takes care about lifecycle events.
    """
    events = Attribute(u"Dict with lifecycle event classes to use for "
                       u"notification.")


class INodeChildValidate(Interface):
    """Part for child node validation.
    """
    allow_non_node_childs = Attribute(u"Flag wether this node may contain non "
                                      u"node based children.")


class INodespaces(Interface):
    """Part for providing nodespaces on node.
    
    A nodespace is a seperate node with special keys - pre- and postfixed with
    ``__`` which gets mapped on storage write operations.
    """
    nodespaces = Attribute(u"Nodespaces.")


class INodify(Interface):
    """Part which hooks node API.
    """


class IOrder(Interface):
    """Reordering support.
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


class IReference(Interface):
    """Holding an internal index of all nodes contained in the tree.
    """
    uuid = Attribute(u"``uuid.UUID`` of this node.")
    index = Attribute(u"The tree node index")
    
    def node(uuid):
        """Return node by uuid located anywhere in this nodetree.
        """


class IStorage(Interface):
    """Provide storage endpoints.
    
    Minimum Storage requirement is described below. An implementation of this
    interface could provide other storage related methods as appropriate.
    """
    
    def __getitem__(key):
        """Return Item from Storage.
        """
    
    def __delitem__(key):
        """Delete Item from storage.
        """
    
    def __setitem__(key, val):
        """Set item to storage.
        """
    
    def __iter__():
        """Iter throught storage keys.
        """


class IUnicode(Interface):
    """XXX: Description of plumbs
    """


class IWrap(Interface):
    """XXX: Description of plumbs
    """


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


class IAttributedComposition(IComposition, IAttributedNode):
    pass


class ILifecycleComposition(IComposition, ILifecycleNode):
    pass

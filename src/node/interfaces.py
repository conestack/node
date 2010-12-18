from zope.interface import Interface, Attribute
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
            interface is not available anyway, so probably nobody will register
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

#try:
#    from node.interfaces import IAliaser
#except ImportError:
#    node = __import__('node.interfaces', {})
#    IAliaser = node.interfaces.IAliaser
# XXX: deprecated message as soon as the new location is stable
#deprecated(
#    'IAliaser',
#    "Will be removed in 2.0, Use node.interfaces.IAliaser instead."
#    )

class INode(ILocation, IFullMapping):
    """A node.
    """
    uuid = Attribute(u"``uuid.UUID`` of this node.")
    path = Attribute(u"Path of node as list")
    root = Attribute(u"Root node")
    index = Attribute(u"The tree node index")
    aliases = Attribute(u"zope.interface.common.mapping.IEnumerableMapping "
                        u"implementation defining key aliases or callable "
                        u"accepting Node as argument. If aliases is None, "
                        u"this feature is disables.")

    def node(uuid):
        """Return node by uuid located anywhere in this nodetree.
        """

    def filtereditems(interface):
        """Return filtered child nodes by interface.
        """

    def insertbefore(newnode, refnode):
        """Insert newnode before refnode.

        __name__ on newnode must be set.

        This function only supports adding of new nodes before the given
        refnode. If you want to move nodes you have to detach them from the
        tree first.
        """

    def insertafter(newnode, refnode):
        """Insert newnode after refnode.

        __name__ on newnode must be set.

        This function only supports adding of new nodes after the given
        refnode. If you want to move nodes you have to detach them from the
        tree first.
        """

    def detach(key):
        """Detach child Node. needed for Node movement.
        """

    def printtree():
        """Debugging helper.
        """


class IRoot(INode):
    """Marker for a root node.
    """


class ILeaf(INode):
    """A node without children.
    """


class ICallableNode(INode):
    """Node which implements the ``__call__`` function.
    """

    def __call__():
        """Expose the tree contents to an output channel.
        """


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
    aliases = Attribute(u"zope.interface.common.mapping.IEnumerableMapping "
                        u"implementation defining attr name aliases or "
                        u"callable accepting NodeAttributes as argument. If "
                        u"aliases is None, this feature is disables. "
                        u"Serves as Whitelist.")

    def __init__(node):
        """Initialize object.

        Takes attributes refering node at creation time.
        """


class IAttributedNode(INode):
    """Node which care about its attributes.
    """
    attributes = Attribute(u"``INodeAttributes`` implementation.")
    attributes_factory = Attribute(u"``INodeAttributes`` implementation class")


class ILifecycleNode(IAttributedNode):
    """Node which care about its lifecycle.
    """
    events = Attribute(u"Dict with lifecycle event classes to use for "
                       u"notification.")


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


class IComposition(INode):
    pass


class IAttributedComposition(IComposition, IAttributedNode):
    pass


class ILifecycleComposition(IComposition, ILifecycleNode):
    pass


# XXX: should we split this up into node.aliasing.interfaces?
# Benefit: the structure would be the same as for modules provided by separate
#          distributions
# rnix: should we really create tons of subpackages?
class IAliaser(Interface):
    """Generic Aliasing Interface
    """
    def alias(key):
        """returns the alias for a key
        """

    def unalias(aliased_key):
        """returns the key belonging to an aliased_key
        """
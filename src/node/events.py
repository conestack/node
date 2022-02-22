from node.behaviors import EventAttribute  # noqa
from node.behaviors import Events
from node.behaviors import suppress_events  # noqa
from node.behaviors import UnknownEvent  # noqa
from node.interfaces import INodeAddedEvent
from node.interfaces import INodeCreatedEvent
from node.interfaces import INodeDetachedEvent
from node.interfaces import INodeModifiedEvent
from node.interfaces import INodeRemovedEvent
from plumber import plumbing
from zope.interface import implementer
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import ObjectRemovedEvent


###############################################################################
# Zope lifecycle events for ILifecycle
###############################################################################

@implementer(INodeCreatedEvent)
class NodeCreatedEvent(ObjectCreatedEvent):
    pass


@implementer(INodeAddedEvent)
class NodeAddedEvent(ObjectAddedEvent):
    pass


@implementer(INodeModifiedEvent)
class NodeModifiedEvent(ObjectModifiedEvent):
    pass


@implementer(INodeRemovedEvent)
class NodeRemovedEvent(ObjectRemovedEvent):
    pass


@implementer(INodeDetachedEvent)
class NodeDetachedEvent(ObjectRemovedEvent):
    pass


###############################################################################
# Event dispatcher using IEvents plumbing behavior
###############################################################################

@plumbing(Events)
class EventDispatcher(object):
    """Object providing event dispatching."""

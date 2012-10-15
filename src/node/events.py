from zope.interface import implementer
from zope.lifecycleevent import (
    ObjectCreatedEvent,
    ObjectAddedEvent,
    ObjectModifiedEvent,
    ObjectRemovedEvent,
)
from .interfaces import (
    INodeCreatedEvent,
    INodeAddedEvent,
    INodeModifiedEvent,
    INodeRemovedEvent,
    INodeDetachedEvent,
)


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

from zope.interface import implements
try:
    from zope.lifecycleevent import (
        ObjectCreatedEvent,
        ObjectAddedEvent,
        ObjectModifiedEvent,
        ObjectRemovedEvent,
    )
except ImportError, e: # BBB
    from zope.app.event.objectevent import ObjectEvent
    class ObjectCreatedEvent(ObjectEvent):
        pass
    class ObjectAddedEvent(ObjectEvent):
        pass
    class ObjectModifiedEvent(ObjectEvent):
        pass
    class ObjectRemovedEvent(ObjectEvent):
        pass

from node.interfaces import (
    INodeCreatedEvent,
    INodeAddedEvent,
    INodeModifiedEvent,
    INodeRemovedEvent,
    INodeDetachedEvent,
)

class NodeCreatedEvent(ObjectCreatedEvent):
    implements(INodeCreatedEvent)
    
class NodeAddedEvent(ObjectAddedEvent):
    implements(INodeAddedEvent)

class NodeModifiedEvent(ObjectModifiedEvent):
    implements(INodeModifiedEvent)

class NodeRemovedEvent(ObjectRemovedEvent):              
    implements(INodeRemovedEvent)

class NodeDetachedEvent(ObjectRemovedEvent):
    implements(INodeDetachedEvent)

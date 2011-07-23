from zope.interface import implements
try:
    from zope.lifecycleevent import (
        ObjectCreatedEvent,
        ObjectAddedEvent,
        ObjectModifiedEvent,
        ObjectRemovedEvent,
    )
except ImportError, e:                                      #pragma NO COVERAGE
    # BBB, XXX: remove this soon, relict from ``zodict``
    from zope.app.event.objectevent import ObjectEvent      #pragma NO COVERAGE
    class ObjectCreatedEvent(ObjectEvent): pass             #pragma NO COVERAGE
    class ObjectAddedEvent(ObjectEvent): pass               #pragma NO COVERAGE
    class ObjectModifiedEvent(ObjectEvent): pass            #pragma NO COVERAGE
    class ObjectRemovedEvent(ObjectEvent): pass             #pragma NO COVERAGE

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
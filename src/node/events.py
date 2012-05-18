from zope.interface import implementer
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


@implementer(INodeCreatedEvent)
class NodeCreatedEvent(ObjectCreatedEvent): pass


@implementer(INodeAddedEvent)
class NodeAddedEvent(ObjectAddedEvent): pass


@implementer(INodeModifiedEvent)
class NodeModifiedEvent(ObjectModifiedEvent): pass


@implementer(INodeRemovedEvent)
class NodeRemovedEvent(ObjectRemovedEvent): pass


@implementer(INodeDetachedEvent)
class NodeDetachedEvent(ObjectRemovedEvent): pass
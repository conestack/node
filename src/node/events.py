from zope.interface import implementer
try:
    from zope.lifecycleevent import ObjectCreatedEvent
    from zope.lifecycleevent import ObjectAddedEvent
    from zope.lifecycleevent import ObjectModifiedEvent
    from zope.lifecycleevent import ObjectRemovedEvent
except ImportError, e:                                      #pragma NO COVERAGE
    # BBB, XXX: remove this soon, relict from ``zodict``
    from zope.app.event.objectevent import ObjectEvent      #pragma NO COVERAGE
    class ObjectCreatedEvent(ObjectEvent): pass             #pragma NO COVERAGE
    class ObjectAddedEvent(ObjectEvent): pass               #pragma NO COVERAGE
    class ObjectModifiedEvent(ObjectEvent): pass            #pragma NO COVERAGE
    class ObjectRemovedEvent(ObjectEvent): pass             #pragma NO COVERAGE
from node.interfaces import INodeCreatedEvent
from node.interfaces import INodeAddedEvent
from node.interfaces import INodeModifiedEvent
from node.interfaces import INodeRemovedEvent
from node.interfaces import INodeDetachedEvent


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
from plumber import (
    default,
    plumb,
    Part,
)
from zope.interface import implements
from node.interfaces import (
    ILifecycle,
    IAttributesLifecycle,
)
from node.parts.attributes import NodeAttributes
try:
    from zope.component.event import objectEventNotify
except ImportError, e:                                       #pragma NO COVERAGE
    # BBB, XXX: remove this soon, relict from ``zodict``
    from zope.app.event.objectevent import objectEventNotify #pragma NO COVERAGE
from node.events import (
    NodeCreatedEvent,
    NodeAddedEvent,
    NodeRemovedEvent,
    NodeModifiedEvent,
    NodeDetachedEvent,
)

class Lifecycle(Part):
    implements(ILifecycle)

    events = default({
        'created': NodeCreatedEvent,
        'added': NodeAddedEvent,
        'modified': NodeModifiedEvent,
        'removed': NodeRemovedEvent,
        'detached': NodeDetachedEvent,
    })

    _notify_suppress = default(False)

    @plumb
    def __init__(_next, self, *args, **kw):
        _next(self, *args, **kw)
        objectEventNotify(self.events['created'](self))

    @plumb
    def __setitem__(_next, self, key, val):
        _next(self, key, val)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['added'](val, newParent=self,
                                               newName=key))

    @plumb
    def __delitem__(_next, self, key):
        delnode = self[key]
        _next(self, key)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['removed'](delnode, oldParent=self,
                                                 oldName=key))
    
    @plumb
    def detach(_next, self, key):
        notify_before = self._notify_suppress
        self._notify_suppress = True
        node = _next(self, key)
        self._notify_suppress = False
        objectEventNotify(self.events['detached'](node, oldParent=self,
                                                  oldName=key))
        return node


class AttributesLifecycle(Part):
    implements(IAttributesLifecycle)

    @plumb
    def __setitem__(_next, self, key, val):
        _next(self, key, val)
        if self.__parent__._notify_suppress:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

    @plumb
    def __delitem__(_next, self, key):
        _next(self, key)
        if self.__parent__._notify_suppress:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

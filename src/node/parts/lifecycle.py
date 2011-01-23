from plumber import (
    plumb,
    default,
    extend,
    Part,
)
from zope.interface import implements
from node.interfaces import ILifecycle
from node.base import OrderedNode
from node.parts.attributes import NodeAttributes
try:
    from zope.component.event import objectEventNotify
except ImportError, e:
    from zope.app.event.objectevent import objectEventNotify # BBB
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

    @plumb
    def __init__(prt, _next, self, *args, **kw):
        _next(self, *args, **kw)
        self._notify_suppress = False
        objectEventNotify(self.events['created'](self))

    @plumb
    def __setitem__(prt, _next, self, key, val):
        _next(self, key, val)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['added'](val, newParent=self,
                                               newName=key))

    @plumb
    def __delitem__(prt, _next, self, key):
        delnode = self[key]
        _next(self, key)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['removed'](delnode, oldParent=self,
                                                 oldName=key))
    
    @plumb
    def detach(prt, _next, self, key):
        notify_before = self._notify_suppress
        self._notify_suppress = True
        node = _next(self, key)
        self._notify_suppress = False
        objectEventNotify(self.events['detached'](node, oldParent=self,
                                                  oldName=key))
        return node


class AttributesLifecycle(Part):

    @plumb
    def __setitem__(prt, _next, self, key, val):
        _next(self, key, val)
        if self.context._notify_suppress:
            return
        objectEventNotify(self.context.events['modified'](self.context))

    @plumb
    def __delitem__(prt, _next, self, key):
        _next(self, key)
        if self.context._notify_suppress:
            return
        objectEventNotify(self.context.events['modified'](self.context))

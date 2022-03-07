from __future__ import absolute_import
from node.events import NodeAddedEvent
from node.events import NodeCreatedEvent
from node.events import NodeDetachedEvent
from node.events import NodeModifiedEvent
from node.events import NodeRemovedEvent
from node.interfaces import IAttributesLifecycle
from node.interfaces import ILifecycle
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.component.event import objectEventNotify
from zope.interface import implementer


@implementer(ILifecycle)
class Lifecycle(Behavior):

    events = default({
        'created': NodeCreatedEvent,
        'added': NodeAddedEvent,
        'modified': NodeModifiedEvent,
        'removed': NodeRemovedEvent,
        'detached': NodeDetachedEvent,
    })

    _notify_suppress = default(False)

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
        objectEventNotify(self.events['created'](self))

    @plumb
    def __setitem__(next_, self, key, val):
        next_(self, key, val)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['added'](
            val,
            newParent=self,
            newName=key
        ))

    @plumb
    def __delitem__(next_, self, key):
        delnode = self[key]
        next_(self, key)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['removed'](
            delnode,
            oldParent=self,
            oldName=key
        ))

    @plumb
    def detach(next_, self, key):
        self._notify_suppress = True
        node = next_(self, key)
        self._notify_suppress = False
        objectEventNotify(self.events['detached'](
            node,
            oldParent=self,
            oldName=key
        ))
        return node


@implementer(IAttributesLifecycle)
class AttributesLifecycle(Behavior):

    @plumb
    def __setitem__(next_, self, key, val):
        next_(self, key, val)
        if self.__parent__._notify_suppress:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

    @plumb
    def __delitem__(next_, self, key):
        next_(self, key)
        if self.__parent__._notify_suppress:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

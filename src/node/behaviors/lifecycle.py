from __future__ import absolute_import
from contextlib import contextmanager
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
import threading


class LifecycleContext(threading.local):
    suppress_events = False


_lifecycle_context = LifecycleContext()


@contextmanager
def suppress_lifecycle_events():
    """Context manager to suppress lifecycle events."""
    _lifecycle_context.suppress_events = True
    try:
        yield
    finally:
        _lifecycle_context.suppress_events = False


@implementer(ILifecycle)
class Lifecycle(Behavior):

    events = default({
        'created': NodeCreatedEvent,
        'added': NodeAddedEvent,
        'modified': NodeModifiedEvent,
        'removed': NodeRemovedEvent,
        'detached': NodeDetachedEvent,
    })

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
        objectEventNotify(self.events['created'](self))

    @plumb
    def __setitem__(next_, self, key, val):
        next_(self, key, val)
        if _lifecycle_context.suppress_events:
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
        if _lifecycle_context.suppress_events:
            return
        objectEventNotify(self.events['removed'](
            delnode,
            oldParent=self,
            oldName=key
        ))

    @plumb
    def detach(next_, self, key):
        with suppress_lifecycle_events():
            node = next_(self, key)
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
        if _lifecycle_context.suppress_events:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

    @plumb
    def __delitem__(next_, self, key):
        next_(self, key)
        if _lifecycle_context.suppress_events:
            return
        objectEventNotify(self.__parent__.events['modified'](self.__parent__))

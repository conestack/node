# -*- coding: utf-8 -*-
from node.interfaces import INodeAddedEvent
from node.interfaces import INodeCreatedEvent
from node.interfaces import INodeDetachedEvent
from node.interfaces import INodeModifiedEvent
from node.interfaces import INodeRemovedEvent
from zope.interface import implementer
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import ObjectRemovedEvent


###############################################################################
# Lifecycle events for ILifecycle
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
# Event dispatcher and event dispatching class attribute descriptor
#
# The API is unabashedly cribbed from Kivy - https://kivy.org
###############################################################################

class UnknownEvent(ValueError):
    """Thrown on attempt to register a subscriber to an unknown event.
    """


class EventDispatcher(object):
    """Object for event dispatching.

    Events are just strings and can be set as class member or registered via
    ``register_event``::

        class ExampleDispatcher(EventDispatcher):
            __events__ = ['event_1']

        dispatcher = ExampleDispatcher()
        dispatcher.register_event('event_2')

    Event subscribers are callables and bound to event name::

        def subscriber(*args, **kw):
            pass  # do something

        dispatcher.bind(event_1=subscriber)

    Events are triggered via ``dispatch``. Given arguments and keyword
    arguments are passed to subscriber::

        dispatcher.dispatch('event_1', 'foo', bar='baz')

    To remove some or all event subscribers from an event dispatcher,
    ``unbind`` is used. Both ``event`` and ``subscriber`` keyword arguments
    are optional::

        dispatcher.unbind(event=event_1, subscriber=subscriber)
    """

    def __init__(self, *args, **kw):
        # do not override events defined on class.
        if not hasattr(self, '__events__'):
            self.__events__ = list()
        # mapping between events and subscribers
        self.__subscribers__ = dict()
        # call super class constructor
        super(EventDispatcher, self).__init__(*args, **kw)
        # iterate class dict and register events for contained EventAttribute
        # objects
        for attr, val in self.__class__.__dict__.items():
            if isinstance(val, EventAttribute):
                self.register_event(attr)
                val.event = attr

    def register_event(self, event):
        """Register event type.

        :param event: Event name as string.
        """
        if not event in self.__events__:
            self.__events__.append(event)

    def bind(self, **kw):
        """Bind subscribers to events.

        :param kw: Each keyword argument is the event name and the argument
            value is the subscriber callable.
        """
        for event, subscriber in kw.items():
            if not event in self.__events__:
                raise UnknownEvent(event)
            subscribers = self.__subscribers__.setdefault(event, list())
            if not subscriber in subscribers:
                subscribers.append(subscriber)

    def unbind(self, event=None, subscriber=None):
        """Unbind subscribers.

        :param event: Event name. If not given, all events are affected.
        :param subscriber: Subscriber callable. If not given, all subscribers
            are affected.
        """
        if event is None and subscriber is None:
            self.__subscribers__ = dict()
        elif event is not None and subscriber is None:
            if event in self.__subscribers__:
                del self.__subscribers__[event]
        elif event is None and subscriber is not None:
            for subscribers in self.__subscribers__.values():
                if subscriber in subscribers:
                    subscribers.remove(subscriber)
        elif event is not None and subscriber is not None:
            subscribers = self.__subscribers__.get(event, list())
            if subscriber in subscribers:
                subscribers.remove(subscriber)

    def dispatch(self, event, *args, **kw):
        """Dispatch event.

        :param event: Event name.
        :param args: Arguments passed to subscribers.
        :patam kw: Keyword arguments passed to subscribers.
        """
        subscribers = self.__subscribers__.get(event, list())
        for subscriber in subscribers:
            subscriber(*args, **kw)


class EventAttribute(object):
    """Descriptor which can be used on ``EventDispatcher`` objects.

    It's possible to bind subscribers to object attributes of type
    ``EventAttribute`` by attribute name::

        class ExampleDispatcher(EventDispatcher):
            example_attribute = EventAttribute(0)

        def subscriber(value):
            pass  # do something

        dispatcher = ExampleDispatcher()
        dispatcher.bind(example_attribute=subscriber)

        # when setting ``example_attribute`` with a changed value, subscriber
        # is called
        dispatcher.example_attribute = 1
    """
    event = None

    def __init__(self, default):
        """Initialize attribute.
        """
        self.value = default

    def __get__(self, obj, owner=None):
        """Return attribute value.
        """
        return self.value

    def __set__(self, obj, value):
        """Set attribute value. Triggers event if value changed.
        """
        dispatch = value != self.value
        self.value = value
        if dispatch:
            obj.dispatch(self.event, value)

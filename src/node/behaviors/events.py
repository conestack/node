# -*- coding: utf-8 -*-
from contextlib import contextmanager
from node.interfaces import IEvents
from node.utils import UNSET
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import plumb
from plumber import plumber
from zope.interface import implementer
import threading

###############################################################################
# Event dispatcher and event dispatching class attribute descriptor
#
# The API is partly cribbed from Kivy - https://kivy.org
###############################################################################


@plumber.metaclasshook
def event_dispatcher_metclass_hook(cls, name, bases, dct):
    """Plumber metaclass hook handling proper post initialization of
    ``EventAttribute`` instances on plumbing classes.
    """
    if not IEvents.implementedBy(cls):
        return
    if not hasattr(cls, '__events__'):
        cls.__events__ = list()
    events = cls.__events__
    for attr, val in dct.items():
        if isinstance(val, EventAttribute):
            if attr not in events:
                events.append(attr)
            val.name = attr


ALL_EVENTS = object()


class suppress_events(object):
    """Context manager to suppress event notification.

    Dedicated to be used in node implementations to internally modify data
    structures and it's not desired that events are dispatched if they
    usually are.

    Suppress all events::

        with suppress_events() as count:
            # count defines the recursion level of ``suppress_event`` calls.
            # do something where normally events are triggered.
            pass

    Suppress specific event::

        with suppress_events('my_event'):
            pass  # do something

    Suppress list of events::

        with suppress_events(['event_1', 'event_2']):
            pass  # do something
    """
    data = threading.local()
    data.suppress = 0
    data.events = list()

    def __init__(self, events=ALL_EVENTS):
        type_ = type(events)
        if type_ not in (list, tuple):
            events = [events]
        for event in events:
            self.data.events.append(event)
        self.events = events

    def __enter__(self):
        self.data.suppress += 1
        return self.data.suppress

    def __exit__(self, type_, value, traceback):
        self.data.suppress -= 1
        for event in self.events:
            self.data.events.remove(event)


class UnknownEvent(ValueError):
    """Thrown on attempt to register a subscriber to an unknown event.
    """


_attribute_subscribers = threading.local()
_attribute_subscribers.subscribers = list()


@contextmanager
def _subscribers(subscribers):
    """Context manager to inject subscribers to ``Events.dispatch``.

    Used in to inject subscribers registered with
    ``EventAttributes.subscriber`` decorator.
    """
    _attribute_subscribers.subscribers = subscribers
    yield


class EventAttribute(object):
    """Descriptor which can be used on ``Events`` behavior using objects.

    It's possible to bind subscribers to object attributes of type
    ``EventAttribute`` by attribute name::

        @plumbing(Events)
        class ExampleDispatcher(object):
            example_attribute = EventAttribute(0)

        def subscriber(value):
            pass  # do something

        dispatcher = ExampleDispatcher()
        dispatcher.bind(example_attribute=subscriber)

    When setting ``example_attribute``, subscriber gets called. By default,
    event is only dispatched if value changes::

        dispatcher.example_attribute = 1

    If it's desired to always dispatch the attribute event when ``__set__``
    gets executed, pass ``always_dispatch`` to constructor::

        @plumbing(Events)
        class ExampleDispatcher(object):
            example_attribute = EventAttribute(0, always_dispatch=True)

    An alternative storage attribute can be given to ``EventAttribute`` at
    creation time to define an alternative container object for the actual
    values. This is useful if it's desired to store the values on node
    attributes for example.::

        @plumbing(Events)
        class ExampleNode(AttributedNode):
            example_attribute = EventAttribute(0, storage='attrs')

    Attribute event subscribers can also be registered with ``subscriber``
    decorator::

        @plumbing(Events)
        class ExampleNode(object):
            example_attribute = EventAttribute(0, storage='attrs')

            @example_attribute.subscriber
            def on_example_attribute(self, value):
                pass  # do something
    """
    name = None

    def __init__(self, default=UNSET,
                 storage='__dict__',
                 always_dispatch=False):
        """Initialize attribute.

        :param default: Default value. Defaults to UNSET
        :param storage: Attribute of instance to use as attribute storage.
            Defaults to ``__dict__``.
        :param always_dispatch: Flag whether events should always be
            dispatched.
        """
        self.default = default
        self.storage = storage
        self.always_dispatch = always_dispatch
        self.subscribers = list()

    def __get__(self, obj, type_=None):
        """Return attribute value.
        """
        if obj is None:
            return self.default
        return getattr(obj, self.storage).get(self.name, self.default)

    def __set__(self, obj, value):
        """Set attribute value. Triggers event if value changed.
        """
        storage = getattr(obj, self.storage)
        old_value = storage.get(self.name, self.default)
        storage[self.name] = value
        if self.always_dispatch or value != old_value:
            with _subscribers(self.subscribers):
                obj.dispatch(self.name, value)

    def __delete__(self, obj):
        """Delete attribute value.
        """
        del getattr(obj, self.storage)[self.name]
        obj.dispatch(self.name, UNSET)

    def subscriber(self, func):
        """Event attribute subscriber decorator.
        """
        self.subscribers.append(func)
        return func


@implementer(IEvents)
class Events(Behavior):
    """Behavior for event dispatching.

    Events are just strings and can be set as class member or registered via
    ``register_event``::

        @plumbing(Events)
        class ExampleDispatcher(object):
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

    @finalize
    def __new__(cls, *args, **kw):
        """Set ``__events__`` and ``__subscribers__`` attributes on instance.
        """
        inst = super(type, cls).__new__(cls, *args, **kw)
        inst.__events__ = list()
        inst.__subscribers__ = dict()
        return inst

    @finalize
    def register_event(self, event):
        """Register event type.

        :param event: Event name as string.
        """
        if event not in self.__events__:
            self.__events__.append(event)

    @finalize
    def bind(self, **kw):
        """Bind subscribers to events.

        :param kw: Each keyword argument is the event name and the argument
            value is the subscriber callable.
        """
        for event, subscriber in kw.items():
            if event not in self.__events__ \
                    and event not in self.__class__.__events__:
                raise UnknownEvent(event)
            subscribers = self.__subscribers__.setdefault(event, list())
            if subscriber not in subscribers:
                subscribers.append(subscriber)

    @finalize
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

    @finalize
    def dispatch(self, event, *args, **kw):
        """Dispatch event.

        :param event: Event name.
        :param args: Arguments passed to subscribers.
        :patam kw: Keyword arguments passed to subscribers.
        """
        attribute_subscribers = _attribute_subscribers.subscribers
        _attribute_subscribers.subscribers = list()
        if suppress_events.data.suppress > 0:
            if ALL_EVENTS in suppress_events.data.events:
                return
            if event in suppress_events.data.events:
                return
        for subscriber in attribute_subscribers:
            subscriber(self, *args, **kw)
        for subscriber in self.__subscribers__.get(event, list()):
            subscriber(*args, **kw)

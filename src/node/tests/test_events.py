from node.base import AttributedNode
from node.events import EventAttribute
from node.events import EventDispatcher
from node.events import UnknownEvent
from node.events import suppress_events
from node.utils import UNSET
from plumber import Behavior
from plumber import default
from plumber import plumbing
import unittest


###############################################################################
# Mock objects
###############################################################################

class Subscriber(object):

    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw


class MyDispatcher(EventDispatcher):
    attr = EventAttribute(1)


class Behavior1(Behavior):
    attr = default(EventAttribute(1))


@plumbing(Behavior1)
class PlumbedDispatcher(EventDispatcher):
    pass


class AttributedDispatcher(AttributedNode, EventDispatcher):
    attr = EventAttribute(1, storage='attrs')


###############################################################################
# Tests
###############################################################################

class TestEvents(unittest.TestCase):

    def test_EventDispatcher_register_event(self):
        dispatcher = EventDispatcher()

        # no events registered yet
        self.assertEqual(dispatcher.__events__, [])

        # register event
        dispatcher.register_event('my_event')
        self.assertEqual(dispatcher.__events__, ['my_event'])

        # register same event again, still just one registration
        dispatcher.register_event('my_event')
        self.assertEqual(dispatcher.__events__, ['my_event'])

    def test_EventDispatcher_bind(self):
        dispatcher = EventDispatcher()

        # no event subscribers registered yet
        self.assertEqual(dispatcher.__subscribers__, {})

        # bind to unknown event
        self.assertRaises(
            UnknownEvent,
            lambda: dispatcher.bind(my_event=Subscriber())
        )

        # register event and bind subscriber to it
        dispatcher.register_event('my_event')
        subscriber = Subscriber()
        dispatcher.bind(my_event=subscriber)

        self.assertEqual(
            dispatcher.__subscribers__,
            {'my_event': [subscriber]}
        )

        # register same subscriber again, still just one Registration
        dispatcher.bind(my_event=subscriber)

        self.assertEqual(
            dispatcher.__subscribers__,
            {'my_event': [subscriber]}
        )

    def test_EventDispatcher_unbind(self):
        dispatcher = EventDispatcher()
        dispatcher.register_event('event_1')
        dispatcher.register_event('event_2')

        subscriber = Subscriber()

        # event is None and subscriber is None
        dispatcher.bind(event_1=subscriber, event_2=subscriber)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [subscriber],
            'event_2': [subscriber]
        })
        dispatcher.unbind()
        self.assertEqual(dispatcher.__subscribers__, {})

        # event is not None and subscriber is None
        dispatcher.bind(event_1=subscriber, event_2=subscriber)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [subscriber],
            'event_2': [subscriber]
        })
        dispatcher.unbind(event='event_1')
        self.assertEqual(dispatcher.__subscribers__, {
            'event_2': [subscriber]
        })
        dispatcher.unbind()

        # event is None and subscriber is not None
        dispatcher.bind(event_1=subscriber, event_2=subscriber)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [subscriber],
            'event_2': [subscriber]
        })
        dispatcher.unbind(subscriber=subscriber)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [],
            'event_2': []
        })
        dispatcher.unbind()

        # event is not None and subscriber is not None
        subscriber_1 = Subscriber()
        subscriber_2 = Subscriber()
        dispatcher.bind(event_1=subscriber_1)
        dispatcher.bind(event_1=subscriber_2)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [subscriber_1, subscriber_2]
        })
        dispatcher.unbind(event='event_1', subscriber=subscriber_1)
        self.assertEqual(dispatcher.__subscribers__, {
            'event_1': [subscriber_2]
        })
        dispatcher.unbind()

    def test_EventDispatcher_dispatch(self):
        dispatcher = EventDispatcher()

        # register event and bind subscriber to it
        dispatcher.register_event('my_event')
        subscriber = Subscriber()
        dispatcher.bind(my_event=subscriber)

        # dispatch event, arguments and keyword arguments are passed to
        # subscriber
        dispatcher.dispatch('my_event', 1, kw=2)
        self.assertEqual(subscriber.args, (1,))
        self.assertEqual(subscriber.kw, dict(kw=2))

    def test_EventAttribute(self):
        dispatcher = MyDispatcher()

        # attribute events get registered automatically and are written to
        # class dict
        self.assertEqual(dispatcher.__class__.__events__, ['attr'])

        # subscribe to attribute change
        subscriber = Subscriber()
        dispatcher.bind(attr=subscriber)

        # if value not changes, no event is triggered
        self.assertEqual(dispatcher.attr, 1)
        dispatcher.attr = 1
        self.assertFalse(hasattr(subscriber, 'args'))

        # if value changes, an event gets triggered
        dispatcher.attr = 2
        self.assertEqual(dispatcher.attr, 2)
        self.assertEqual(subscriber.args, (2,))

        dispatcher.attr = 3
        self.assertEqual(dispatcher.attr, 3)
        self.assertEqual(subscriber.args, (3,))

        # default value on class still 1
        self.assertEqual(MyDispatcher.attr, 1)

        # __del__ removes attribute from storage and triggers event with UNSET
        # as value.
        self.assertEqual(dispatcher.__dict__['attr'], 3)
        del dispatcher.attr
        self.assertEqual(subscriber.args, (UNSET,))
        self.assertFalse('attr' in dispatcher.__dict__)

        # After deleting the default value of event attribute is returned again
        self.assertEqual(dispatcher.attr, 1)

    def test_EventAttribute_storage(self):
        dispatcher = AttributedDispatcher()
        subscriber = Subscriber()
        dispatcher.bind(attr=subscriber)

        dispatcher.attr = 0
        self.assertEqual(subscriber.args, (0,))
        self.assertEqual(dispatcher.attrs['attr'], 0)
        self.assertFalse('attr' in dispatcher.__dict__)

        del dispatcher.attr
        self.assertEqual(subscriber.args, (UNSET,))
        self.assertFalse('attr' in dispatcher.attrs)

    def test_suppress_events(self):
        dispatcher = MyDispatcher()
        dispatcher.register_event('my_event')

        subscriber = Subscriber()
        dispatcher.bind(my_event=subscriber, attr=subscriber)

        with suppress_events():
            dispatcher.attr = 0
        self.assertFalse(hasattr(subscriber, 'args'))

        with suppress_events('attr'):
            dispatcher.attr = 1
        self.assertFalse(hasattr(subscriber, 'args'))

        with suppress_events(['other']):
            dispatcher.attr = 2
        self.assertEqual(subscriber.args, (2,))
        del subscriber.args

        with suppress_events():
            dispatcher.dispatch('my_event', 0)
        self.assertFalse(hasattr(subscriber, 'args'))

        with suppress_events('my_event'):
            dispatcher.dispatch('my_event', 1)
        self.assertFalse(hasattr(subscriber, 'args'))

        with suppress_events(['other']):
            dispatcher.dispatch('my_event', 2)
        self.assertEqual(subscriber.args, (2,))

    def test_with_plumber(self):
        dispatcher = PlumbedDispatcher()
        subscriber = Subscriber()
        dispatcher.bind(attr=subscriber)

        dispatcher.attr = 0
        self.assertEqual(subscriber.args, (0,))

from node.events import EventAttribute
from node.events import EventDispatcher
from node.events import UnknownEvent
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

        # attribute events get registered automatically
        self.assertEqual(dispatcher.__events__, ['attr'])

        # subscribe to attribute change
        subscriber = Subscriber()
        dispatcher.bind(attr=subscriber)

        # if value not changes, no event is triggered
        self.assertEqual(dispatcher.attr, 1)
        dispatcher.attr = 1
        self.assertFalse(hasattr(subscriber, 'args'))
        self.assertFalse(hasattr(subscriber, 'kw'))

        # if value changes, an event gets triggered
        dispatcher.attr = 2
        self.assertEqual(subscriber.args, (2,))
        self.assertEqual(subscriber.kw, {})

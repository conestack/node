from node.behaviors import Attributes
from node.behaviors import AttributesLifecycle
from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import Lifecycle
from node.behaviors import NodeAttributes
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.events import NodeAddedEvent
from node.events import NodeCreatedEvent
from node.events import NodeDetachedEvent
from node.events import NodeModifiedEvent
from node.events import NodeRemovedEvent
from node.interfaces import INode
from node.interfaces import INodeAddedEvent
from node.interfaces import INodeCreatedEvent
from node.interfaces import INodeDetachedEvent
from node.interfaces import INodeModifiedEvent
from node.interfaces import INodeRemovedEvent
from node.tests import NodeTestCase
from plumber import plumbing
import zope.component


###############################################################################
# Mock objects
###############################################################################

class Handler(object):
    handled = []

    def __call__(self, obj, event):
        self.handled.append(event)

    def clear(self):
        self.handled = []


@plumbing(
    DefaultInit,
    Nodify,
    DictStorage)
class NoLifecycleNode(object):
    pass


@plumbing(AttributesLifecycle)
class LifecycleNodeAttributes(NodeAttributes):
    pass


@plumbing(
    Nodespaces,
    Attributes,
    Lifecycle,
    DefaultInit,
    Nodify,
    DictStorage)
class LifecycleNode(object):
    attributes_factory = LifecycleNodeAttributes


###############################################################################
# Tests
###############################################################################

class TestLifecycle(NodeTestCase):

    def setUp(self):
        super(TestLifecycle, self).setUp()
        handler = self.handler = Handler()
        zope.component.provideHandler(handler, [INode, INodeCreatedEvent])
        zope.component.provideHandler(handler, [INode, INodeAddedEvent])
        zope.component.provideHandler(handler, [INode, INodeModifiedEvent])
        zope.component.provideHandler(handler, [INode, INodeRemovedEvent])
        zope.component.provideHandler(handler, [INode, INodeDetachedEvent])

    def test_NodeCreatedEvent(self):
        # Check NodeCreation
        self.handler.clear()

        NoLifecycleNode(name='no_notify')
        self.assertEqual(self.handler.handled, [])

        LifecycleNode(name='root')
        self.assertEqual(len(self.handler.handled), 1)
        self.assertTrue(isinstance(self.handler.handled[0], NodeCreatedEvent))

        self.handler.clear()

    def test_NodeAddedEvent(self):
        # Check Node adding
        root = LifecycleNode(name='root')

        self.handler.clear()

        root['child1'] = LifecycleNode()
        self.assertEqual(len(self.handler.handled), 2)
        self.assertTrue(isinstance(self.handler.handled[0], NodeCreatedEvent))
        self.assertTrue(isinstance(self.handler.handled[1], NodeAddedEvent))

        self.handler.clear()

    def test_NodeModifiedEvent(self):
        # Check Node modification
        root = LifecycleNode(name='root')
        child = root['child'] = LifecycleNode()

        self.handler.clear()

        # No event, despite the node creation for the attributes nodespace
        attrs = child.attrs
        self.assertTrue(isinstance(attrs, LifecycleNodeAttributes))
        self.assertEqual(len(self.handler.handled), 0)

        self.handler.clear()

        # Node modified events if the attributes nodespace is changed
        child.attrs['foo'] = 1
        self.assertEqual(len(self.handler.handled), 1)
        self.assertTrue(isinstance(self.handler.handled[0], NodeModifiedEvent))

        self.handler.clear()

        del child.attrs['foo']
        self.assertEqual(len(self.handler.handled), 1)
        self.assertTrue(isinstance(self.handler.handled[0], NodeModifiedEvent))

        self.handler.clear()

    def test_NodeRemovedEvent(self):
        # Check Node Deletion
        root = LifecycleNode(name='root')
        root['child'] = LifecycleNode()

        self.handler.clear()

        del root['child']
        self.assertEqual(len(self.handler.handled), 1)
        self.assertTrue(isinstance(self.handler.handled[0], NodeRemovedEvent))

        self.handler.clear()

    def test_NodeDetachedEvent(self):
        # Check Node Detach
        root = LifecycleNode(name='root')
        root['child'] = LifecycleNode()

        self.handler.clear()

        root.detach('child')
        self.assertEqual(len(self.handler.handled), 1)
        self.assertTrue(isinstance(self.handler.handled[0], NodeDetachedEvent))

        self.handler.clear()

    def test__notify_suppress(self):
        # Check notify suppress on ``__setitem__``
        root = LifecycleNode(name='root')

        self.handler.clear()

        root._notify_suppress = True
        root['child'] = NoLifecycleNode()
        self.assertEqual(len(self.handler.handled), 0)

        # Check notify suppress on attributes manipulation
        attrs = root.attrs
        attrs['foo'] = 'foo'
        self.assertEqual(len(self.handler.handled), 0)

        del attrs['foo']
        self.assertEqual(len(self.handler.handled), 0)

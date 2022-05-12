from node.behaviors import DefaultInit
from node.behaviors import Node
from node.behaviors import NodeInit
from node.interfaces import IDefaultInit
from node.interfaces import INode
from node.interfaces import INodeInit
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import Interface


###############################################################################
# Mock objects
###############################################################################

@plumbing(DefaultInit)
class DefaultInitObject(object):
    pass


@plumbing(NodeInit)
class NodeInitObject(object):

    def __init__(self, foo, bar=None):
        self.foo = foo
        self.bar = bar


@plumbing(DefaultInit, Node)
class NodeObject(object):
    pass


class NoInterface(Interface):
    pass


###############################################################################
# Tests
###############################################################################

class TestNode(NodeTestCase):

    def test_DefaultInit(self):
        obj = DefaultInitObject(name='name', parent='parent')
        self.assertTrue(IDefaultInit.providedBy(obj))
        self.assertEqual(obj.__name__, 'name')
        self.assertEqual(obj.__parent__, 'parent')

    def test_NodeInit(self):
        obj = NodeInitObject('foo', name='name', parent='parent', bar='bar')
        self.assertTrue(INodeInit.providedBy(obj))
        self.assertEqual(obj.__name__, 'name')
        self.assertEqual(obj.__parent__, 'parent')
        self.assertEqual(obj.foo, 'foo')
        self.assertEqual(obj.bar, 'bar')

    def test_Node(self):
        parent = NodeObject(name='parent')
        node = NodeObject(name='node', parent=parent)

        # interface
        self.assertTrue(INode.providedBy(node))

        # __name__
        self.assertEqual(node.__name__, 'node')
        self.assertEqual(node.name, 'node')
        with self.assertRaises(AttributeError):
            node.name = ''

        # __parent__
        self.assertEqual(node.__parent__, parent)
        self.assertEqual(node.parent, parent)
        with self.assertRaises(AttributeError):
            node.parent = None

        # path
        self.assertEqual(node.path, ['parent', 'node'])

        # root
        self.assertEqual(node.root, parent)

        # acquire
        self.assertEqual(node.acquire(NoInterface), None)
        self.assertEqual(node.acquire(INode), parent)
        self.assertEqual(node.acquire(NodeObject), parent)

        # __nonzero__, __bool__
        self.assertTrue(bool(node))

        # __repr__, __str__
        self.checkOutput("""
        <NodeObject object 'node' at ...>
        """, str(node))

        # noderepr
        self.assertEqual(
            node.noderepr,
            "<class 'node.tests.test_node.NodeObject'>: node"
        )

from node.behaviors.node import DefaultInit
from node.behaviors.node import Node
from node.interfaces import INode
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import Interface


###############################################################################
# Mock objects
###############################################################################

@plumbing(DefaultInit)
class DefaultInitObject(object):
    pass


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
        self.assertEqual(obj.__name__, 'name')
        self.assertEqual(obj.__parent__, 'parent')

    def test_Node(self):
        parent = NodeObject(name='parent')
        node = NodeObject(name='node', parent=parent)

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

from node.behaviors import DefaultInit
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import MappingReference
from node.behaviors import OdictStorage
from node.behaviors import Order
from node.tests import NodeTestCase
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    MappingAdopt,
    Order,
    DefaultInit,
    MappingNode,
    OdictStorage)
class OrderableNode(object):
    pass


@plumbing(
    MappingAdopt,
    Order,
    MappingReference,
    DefaultInit,
    MappingNode,
    OdictStorage)
class OrderReferenceNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestOrder(NodeTestCase):

    def test_first_key(self):
        node = OrderableNode(name='root')
        with self.assertRaises(KeyError):
            node.first_key
        node['0'] = OrderableNode()
        self.assertEqual(node.first_key, '0')
        node['1'] = OrderableNode()
        self.assertEqual(node.first_key, '0')

    def test_last_key(self):
        node = OrderableNode(name='root')
        with self.assertRaises(KeyError):
            node.last_key
        node['0'] = OrderableNode()
        self.assertEqual(node.last_key, '0')
        node['1'] = OrderableNode()
        self.assertEqual(node.last_key, '1')

    def test_next_key(self):
        node = OrderableNode(name='root')
        with self.assertRaises(KeyError):
            node.next_key('x')
        node['x'] = OrderableNode()
        with self.assertRaises(KeyError):
            node.next_key('x')
        node['y'] = OrderableNode()
        self.assertEqual(node.next_key('x'), 'y')

    def test_prev_key(self):
        node = OrderableNode()
        with self.assertRaises(KeyError):
            node.prev_key('x')
        node['x'] = OrderableNode()
        with self.assertRaises(KeyError):
            node.prev_key('x')
        node['y'] = OrderableNode()
        self.assertEqual(node.prev_key('y'), 'x')

    def test_swap(self):
        # Test ``swap``
        node = OrderableNode(name='root')
        node['0'] = OrderableNode()
        node['1'] = OrderableNode()
        node['2'] = OrderableNode()
        node['3'] = OrderableNode()
        node['4'] = OrderableNode()
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case first 2, a < b
        node.swap(node['0'], node['1'])
        self.assertEqual(list(node.keys()), ['1', '0', '2', '3', '4'])

        # Case first 2, a > b
        node.swap(node['0'], node['1'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case last 2, a < b
        node.swap(node['3'], node['4'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '4', '3'])

        # Case last 2, a > b
        node.swap(node['3'], node['4'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case neighbors, a < b
        node.swap(node['1'], node['2'])
        self.assertEqual(list(node.keys()), ['0', '2', '1', '3', '4'])

        # Case neighbors, a > b
        node.swap(node['1'], node['2'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case non neighbors, one node first, a < b
        node.swap(node['0'], node['2'])
        self.assertEqual(list(node.keys()), ['2', '1', '0', '3', '4'])

        # Case non neighbors, one node first, a > b
        node.swap(node['0'], node['2'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case non neighbors, one node last, a < b
        node.swap(node['2'], node['4'])
        self.assertEqual(list(node.keys()), ['0', '1', '4', '3', '2'])

        # Case non neighbors, one node last, a > b
        node.swap(node['2'], node['4'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

        # Case non neighbors, a < b
        node.swap(node['1'], node['3'])
        self.assertEqual(list(node.keys()), ['0', '3', '2', '1', '4'])

        # Case non neighbors, a > b
        node.swap(node['1'], node['3'])
        self.assertEqual(list(node.keys()), ['0', '1', '2', '3', '4'])

    def test_insertbefore(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()

        node.insertbefore(OrderableNode(name='child2'), node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        node.insertbefore(OrderableNode(name='child3'), 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        with self.assertRaises(ValueError) as arc:
            node.insertbefore(
                OrderableNode(name='new'),
                OrderableNode(name='ref')
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertafter(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()

        node.insertafter(OrderableNode(name='child2'), node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

        node.insertafter(OrderableNode(name='child3'), 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

        with self.assertRaises(ValueError) as arc:
            node.insertafter(
                OrderableNode(name='new'),
                OrderableNode(name='ref')
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertfirst(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()

        node.insertfirst(OrderableNode(name='child2'))
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

    def test_insertlast(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()

        node.insertlast(OrderableNode(name='child2'))
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

    def test_movebefore(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        node.movebefore(node['child2'], node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        node.movebefore('child1', 'child2')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

    def test_moveafter(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        node.moveafter(node['child1'], node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        node.moveafter('child2', 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

    def test_movefirst(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        node.movefirst(node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        node.movefirst('child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

    def test_movelast(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        node.movelast(node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

        node.movelast('child2')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

    def test_validateinsertion(self):
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()

        new = OrderableNode()
        with self.assertRaises(ValueError) as arc:
            node.insertafter(new, node['child1'])
        self.assertEqual(str(arc.exception), 'Given node has no __name__ set.')

        new.__name__ = 'child1'
        with self.assertRaises(KeyError) as arc:
            node.insertafter(new, node['child1'])
        self.assertEqual(
            str(arc.exception),
            "'Tree already contains node with name child1'"
        )

    def test_detach_and_add(self):
        # Old way of moving a node. We first need to detach the node we want to
        # move from tree. Then insert the detached node elsewhere. In general,
        # you can insert the detached node or subtree to a complete different
        # tree
        node = OrderableNode(name='root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        detached = node.detach('child1')
        node.insertafter(detached, node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
        ))

    def test_order_with_references(self):
        node = OrderReferenceNode(name='root')
        node['child1'] = OrderReferenceNode()
        node['child3'] = OrderReferenceNode()
        node['child4'] = OrderReferenceNode()
        node['child2'] = OrderReferenceNode()
        node['child5'] = OrderReferenceNode()

        self.assertEqual(len(node._index.keys()), 6)

        with self.assertRaises(KeyError) as arc:
            node.insertbefore(node['child2'], node['child1'])
        self.assertEqual(
            str(arc.exception),
            "'Tree already contains node with name child2'"
        )

        self.assertEqual(len(node._index.keys()), 6)
        detached = node.detach('child4')
        self.assertEqual(detached.name, 'child4')
        self.assertEqual(len(detached._index.keys()), 1)
        self.assertEqual(len(node._index.keys()), 5)
        self.assertEqual(len(node.values()), 4)

        node.insertbefore(detached, node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: root\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: child5\n"
        ))

        # Merge 2 Node Trees
        tree1 = OrderReferenceNode()
        tree1['a'] = OrderReferenceNode()
        tree1['b'] = OrderReferenceNode()
        tree2 = OrderReferenceNode()
        tree2['d'] = OrderReferenceNode()
        tree2['e'] = OrderReferenceNode()

        self.assertFalse(tree1._index is tree2._index)
        self.assertEqual(len(tree1._index.keys()), 3)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: b\n"
        ))

        self.assertEqual(len(tree2._index.keys()), 3)
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

        tree1['c'] = tree2
        self.assertEqual(len(tree1._index.keys()), 6)
        self.assertTrue(tree1._index is tree2._index)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: b\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: c\n"
            "    <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

        # Detach subtree and insert elsewhere
        sub = tree1.detach('c')
        self.assertEqual(sub.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: c\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))
        self.assertFalse(tree1._index is sub._index)
        self.assertTrue(sub._index is sub['d']._index is sub['e']._index)
        self.assertEqual(len(sub._index.keys()), 3)

        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: b\n"
        ))
        self.assertEqual(len(tree1._index.keys()), 3)

        sub.__name__ = 'x'
        tree1.insertbefore(sub, tree1['a'])
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: x\n"
            "    <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: b\n"
        ))
        self.assertTrue(tree1._index is sub._index)
        self.assertEqual(len(tree1._index.keys()), 6)

        with self.assertRaises(KeyError) as arc:
            tree1.insertbefore(sub, tree1['a'])
        self.assertEqual(
            str(arc.exception),
            "'Tree already contains node with name x'"
        )

        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

        tree2['d'].child_constraints = None
        tree2['d']['a'] = object()
        self.checkOutput("""\
        <class 'node.tests.test_order.OrderReferenceNode'>: x
        __<class 'node.tests.test_order.OrderReferenceNode'>: d
        ____a: <object object at ...>
        __<class 'node.tests.test_order.OrderReferenceNode'>: e
        """, tree2.treerepr(prefix='_'))

        tree2.detach('d')
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

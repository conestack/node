from node.behaviors import ListStorage
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import MappingOrder
from node.behaviors import MappingReference
from node.behaviors import NodeInit
from node.behaviors import OdictStorage
from node.behaviors import SequenceAdopt
from node.behaviors import SequenceNode
from node.behaviors import SequenceOrder
from node.behaviors import SequenceReference
from node.tests import NodeTestCase
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    NodeInit,
    MappingAdopt,
    MappingOrder,
    MappingNode,
    OdictStorage)
class OrderableMappingNode(object):
    pass


@plumbing(
    NodeInit,
    MappingAdopt,
    MappingOrder,
    MappingReference,
    MappingNode,
    OdictStorage)
class OrderReferenceMappingNode(object):
    pass


@plumbing(
    NodeInit,
    SequenceAdopt,
    SequenceOrder,
    SequenceNode,
    ListStorage)
class OrderableSequenceNode(object):
    pass


@plumbing(
    NodeInit,
    SequenceAdopt,
    SequenceOrder,
    SequenceReference,
    SequenceNode,
    ListStorage)
class OrderReferenceSequenceNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestMappingOrder(NodeTestCase):

    def test_first_key(self):
        node = OrderableMappingNode(name='root')
        with self.assertRaises(KeyError):
            node.first_key
        node['0'] = OrderableMappingNode()
        self.assertEqual(node.first_key, '0')
        node['1'] = OrderableMappingNode()
        self.assertEqual(node.first_key, '0')

    def test_last_key(self):
        node = OrderableMappingNode(name='root')
        with self.assertRaises(KeyError):
            node.last_key
        node['0'] = OrderableMappingNode()
        self.assertEqual(node.last_key, '0')
        node['1'] = OrderableMappingNode()
        self.assertEqual(node.last_key, '1')

    def test_next_key(self):
        node = OrderableMappingNode(name='root')
        with self.assertRaises(KeyError):
            node.next_key('x')
        node['x'] = OrderableMappingNode()
        with self.assertRaises(KeyError):
            node.next_key('x')
        node['y'] = OrderableMappingNode()
        self.assertEqual(node.next_key('x'), 'y')

    def test_prev_key(self):
        node = OrderableMappingNode()
        with self.assertRaises(KeyError):
            node.prev_key('x')
        node['x'] = OrderableMappingNode()
        with self.assertRaises(KeyError):
            node.prev_key('x')
        node['y'] = OrderableMappingNode()
        self.assertEqual(node.prev_key('y'), 'x')

    def test_swap(self):
        # Test ``swap``
        node = OrderableMappingNode(name='root')
        node['0'] = OrderableMappingNode()
        node['1'] = OrderableMappingNode()
        node['2'] = OrderableMappingNode()
        node['3'] = OrderableMappingNode()
        node['4'] = OrderableMappingNode()
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
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()

        node.insertbefore(OrderableMappingNode(name='child2'), node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        node.insertbefore(OrderableMappingNode(name='child3'), 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        with self.assertRaises(ValueError) as arc:
            node.insertbefore(
                OrderableMappingNode(name='new'),
                OrderableMappingNode(name='ref')
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertafter(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()

        node.insertafter(OrderableMappingNode(name='child2'), node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

        node.insertafter(OrderableMappingNode(name='child3'), 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

        with self.assertRaises(ValueError) as arc:
            node.insertafter(
                OrderableMappingNode(name='new'),
                OrderableMappingNode(name='ref')
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertfirst(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()

        node.insertfirst(OrderableMappingNode(name='child2'))
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

    def test_insertlast(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()

        node.insertlast(OrderableMappingNode(name='child2'))
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

    def test_movebefore(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()
        node['child2'] = OrderableMappingNode()

        node.movebefore(node['child2'], node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        node.movebefore('child1', 'child2')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

    def test_moveafter(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()
        node['child2'] = OrderableMappingNode()

        node.moveafter(node['child1'], node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        node.moveafter('child2', 'child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

    def test_movefirst(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()
        node['child2'] = OrderableMappingNode()

        node.movefirst(node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        node.movefirst('child1')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

    def test_movelast(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()
        node['child2'] = OrderableMappingNode()

        node.movelast(node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

        node.movelast('child2')
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
        ))

    def test_validateinsertion(self):
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()

        new = OrderableMappingNode()
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
        node = OrderableMappingNode(name='root')
        node['child1'] = OrderableMappingNode()
        node['child2'] = OrderableMappingNode()

        detached = node.detach('child1')
        node.insertafter(detached, node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableMappingNode'>: child1\n"
        ))

    def test_order_with_references(self):
        node = OrderReferenceMappingNode(name='root')
        node['child1'] = OrderReferenceMappingNode()
        node['child3'] = OrderReferenceMappingNode()
        node['child4'] = OrderReferenceMappingNode()
        node['child2'] = OrderReferenceMappingNode()
        node['child5'] = OrderReferenceMappingNode()

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
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: root\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: child5\n"
        ))

        # Merge 2 Node Trees
        tree1 = OrderReferenceMappingNode()
        tree1['a'] = OrderReferenceMappingNode()
        tree1['b'] = OrderReferenceMappingNode()
        tree2 = OrderReferenceMappingNode()
        tree2['d'] = OrderReferenceMappingNode()
        tree2['e'] = OrderReferenceMappingNode()

        self.assertFalse(tree1._index is tree2._index)
        self.assertEqual(len(tree1._index.keys()), 3)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: b\n"
        ))

        self.assertEqual(len(tree2._index.keys()), 3)
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
        ))

        tree1['c'] = tree2
        self.assertEqual(len(tree1._index.keys()), 6)
        self.assertTrue(tree1._index is tree2._index)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: b\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: c\n"
            "    <class 'node.tests.test_order.OrderReferenceMappingNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
        ))

        # Detach subtree and insert elsewhere
        sub = tree1.detach('c')
        self.assertEqual(sub.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: c\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
        ))
        self.assertFalse(tree1._index is sub._index)
        self.assertTrue(sub._index is sub['d']._index is sub['e']._index)
        self.assertEqual(len(sub._index.keys()), 3)

        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: b\n"
        ))
        self.assertEqual(len(tree1._index.keys()), 3)

        sub.__name__ = 'x'
        tree1.insertbefore(sub, tree1['a'])
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: x\n"
            "    <class 'node.tests.test_order.OrderReferenceMappingNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: b\n"
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
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
        ))

        tree2['d'].child_constraints = None
        tree2['d']['a'] = object()
        self.checkOutput("""\
        <class 'node.tests.test_order.OrderReferenceMappingNode'>: x
        __<class 'node.tests.test_order.OrderReferenceMappingNode'>: d
        ____a: <object object at ...>
        __<class 'node.tests.test_order.OrderReferenceMappingNode'>: e
        """, tree2.treerepr(prefix='_'))

        tree2.detach('d')
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceMappingNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceMappingNode'>: e\n"
        ))


class TestSequenceOrder(NodeTestCase):

    def test_first_index(self):
        node = OrderableSequenceNode(name='root')
        with self.assertRaises(IndexError):
            node.first_index
        node.append(OrderableSequenceNode())
        self.assertEqual(node.first_index, 0)
        node.append(OrderableSequenceNode())
        self.assertEqual(node.first_index, 0)

    def test_last_index(self):
        node = OrderableSequenceNode(name='root')
        with self.assertRaises(IndexError):
            node.last_index
        node.append(OrderableSequenceNode())
        self.assertEqual(node.last_index, 0)
        node.append(OrderableSequenceNode())
        self.assertEqual(node.last_index, 1)

    def test_next_index(self):
        node = OrderableSequenceNode(name='root')
        with self.assertRaises(IndexError):
            node.next_index(0)
        node.append(OrderableSequenceNode())
        with self.assertRaises(IndexError):
            node.next_index(0)
        node.append(OrderableSequenceNode())
        self.assertEqual(node.next_index(0), 1)

    def test_prev_index(self):
        node = OrderableSequenceNode()
        with self.assertRaises(IndexError):
            node.prev_index(0)
        node.append(OrderableSequenceNode())
        with self.assertRaises(IndexError):
            node.prev_index(0)
        node.append(OrderableSequenceNode())
        self.assertEqual(node.prev_index(1), 0)

    def test_swap(self):
        # Test ``swap``
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        child_3 = OrderableSequenceNode()
        child_4 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)
        node.append(child_3)
        node.append(child_4)

        # Case first 2, a < b
        node.swap(node['0'], node['1'])
        self.assertEqual(
            [child for child in node],
            [child_1, child_0, child_2, child_3, child_4]
        )

        # Case first 2, a > b
        node.swap(node['0'], node['1'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

        # Case last 2, a < b
        node.swap(node['3'], node['4'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_4, child_3]
        )

        # Case last 2, a > b
        node.swap(node['3'], node['4'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

        # Case neighbors, a < b
        node.swap(node['1'], node['2'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_2, child_1, child_3, child_4]
        )

        # Case neighbors, a > b
        node.swap(node['1'], node['2'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

        # Case non neighbors, one node first, a < b
        node.swap(node['0'], node['2'])
        self.assertEqual(
            [child for child in node],
            [child_2, child_1, child_0, child_3, child_4]
        )

        # Case non neighbors, one node first, a > b
        node.swap(node['0'], node['2'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

        # Case non neighbors, one node last, a < b
        node.swap(node['2'], node['4'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_4, child_3, child_2]
        )

        # Case non neighbors, one node last, a > b
        node.swap(node['2'], node['4'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

        # Case non neighbors, a < b
        node.swap(node['1'], node['3'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_3, child_2, child_1, child_4]
        )

        # Case non neighbors, a > b
        node.swap(node['1'], node['3'])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2, child_3, child_4]
        )

    def test_insertbefore(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        node.append(child_0)

        child_1 = OrderableSequenceNode()
        node.insertbefore(child_1, node[0])
        self.assertEqual(
            [child for child in node],
            [child_1, child_0]
        )

        child_2 = OrderableSequenceNode()
        node.insertbefore(child_2, '1')
        self.assertEqual(
            [child for child in node],
            [child_1, child_2, child_0]
        )

        with self.assertRaises(ValueError) as arc:
            node.insertbefore(
                OrderableSequenceNode(),
                OrderableSequenceNode()
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertafter(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        node.append(child_0)

        child_1 = OrderableSequenceNode()
        node.insertafter(child_1, node[0])
        self.assertEqual(
            [child for child in node],
            [child_0, child_1]
        )

        child_2 = OrderableSequenceNode()
        node.insertafter(child_2, 0)
        self.assertEqual(
            [child for child in node],
            [child_0, child_2, child_1]
        )

        with self.assertRaises(ValueError) as arc:
            node.insertafter(
                OrderableSequenceNode(),
                OrderableSequenceNode()
            )
        self.assertEqual(
            str(arc.exception),
            'Given reference node not child of self.'
        )

    def test_insertfirst(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        node.append(child_0)

        child_1 = OrderableSequenceNode()
        node.insertfirst(child_1)
        self.assertEqual(
            [child for child in node],
            [child_1, child_0]
        )

    def test_insertlast(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        node.append(child_0)

        child_1 = OrderableSequenceNode()
        node.insertlast(child_1)
        self.assertEqual(
            [child for child in node],
            [child_0, child_1]
        )

    def test_movebefore(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)

        node.movebefore(child_1, child_0)
        self.assertEqual(
            [child for child in node],
            [child_1, child_0, child_2]
        )

        node.movebefore(child_2, child_1)
        self.assertEqual(
            [child for child in node],
            [child_2, child_1, child_0]
        )

        node.movebefore(child_1, child_2)
        self.assertEqual(
            [child for child in node],
            [child_1, child_2, child_0]
        )

        node.movebefore(child_1, child_0)
        self.assertEqual(
            [child for child in node],
            [child_2, child_1, child_0]
        )

    def test_moveafter(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)

        node.moveafter(child_0, child_1)
        self.assertEqual(
            [child for child in node],
            [child_1, child_0, child_2]
        )

        node.moveafter(child_1, child_2)
        self.assertEqual(
            [child for child in node],
            [child_0, child_2, child_1]
        )

        node.moveafter(child_2, child_1)
        self.assertEqual(
            [child for child in node],
            [child_0, child_1, child_2]
        )

        node.moveafter(child_2, child_0)
        self.assertEqual(
            [child for child in node],
            [child_0, child_2, child_1]
        )

    def test_movefirst(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)

        node.movefirst(child_1)
        self.assertEqual(
            [child for child in node],
            [child_1, child_0, child_2]
        )
        node.movefirst(child_2)
        self.assertEqual(
            [child for child in node],
            [child_2, child_1, child_0]
        )

    def _test_movelast(self):
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)

        node.movelast(child_0)
        self.assertEqual(
            [child for child in node],
            [child_1, child_2, child_0]
        )

        node.movelast(child_2)
        self.assertEqual(
            [child for child in node],
            [child_1, child_0, child_2]
        )

    def test_lookup_node_index(self):
        node = OrderableSequenceNode(name='root')
        node.append(OrderableSequenceNode())
        node.append(OrderableSequenceNode())

        with self.assertRaises(ValueError):
            node._lookup_node_index(OrderableSequenceNode())
        with self.assertRaises(ValueError):
            node._lookup_node_index('-1')
        with self.assertRaises(ValueError):
            node._lookup_node_index(-1)
        with self.assertRaises(ValueError):
            node._lookup_node_index('2')
        with self.assertRaises(ValueError):
            node._lookup_node_index(2)
        self.assertEqual(node._lookup_node_index(node[0]), 0)
        self.assertEqual(node._lookup_node_index(node[1]), 1)
        self.assertEqual(node._lookup_node_index('0'), 0)
        self.assertEqual(node._lookup_node_index(1), 1)

    def test_detach_and_add(self):
        # Old way of moving a node. We first need to detach the node we want to
        # move from tree. Then insert the detached node elsewhere. In general,
        # you can insert the detached node or subtree to a complete different
        # tree
        node = OrderableSequenceNode(name='root')
        child_0 = OrderableSequenceNode()
        child_1 = OrderableSequenceNode()
        child_2 = OrderableSequenceNode()
        node.append(child_0)
        node.append(child_1)
        node.append(child_2)

        detached = node.detach(0)
        node.insertafter(detached, 1)
        self.assertEqual(
            [child for child in node],
            [child_1, child_2, child_0]
        )

    def _test_order_with_references(self):
        node = OrderReferenceSequenceNode(name='root')
        node['child1'] = OrderReferenceSequenceNode()
        node['child3'] = OrderReferenceSequenceNode()
        node['child4'] = OrderReferenceSequenceNode()
        node['child2'] = OrderReferenceSequenceNode()
        node['child5'] = OrderReferenceSequenceNode()

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
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: root\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: child5\n"
        ))

        # Merge 2 Node Trees
        tree1 = OrderReferenceSequenceNode()
        tree1['a'] = OrderReferenceSequenceNode()
        tree1['b'] = OrderReferenceSequenceNode()
        tree2 = OrderReferenceSequenceNode()
        tree2['d'] = OrderReferenceSequenceNode()
        tree2['e'] = OrderReferenceSequenceNode()

        self.assertFalse(tree1._index is tree2._index)
        self.assertEqual(len(tree1._index.keys()), 3)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: b\n"
        ))

        self.assertEqual(len(tree2._index.keys()), 3)
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
        ))

        tree1['c'] = tree2
        self.assertEqual(len(tree1._index.keys()), 6)
        self.assertTrue(tree1._index is tree2._index)
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: b\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: c\n"
            "    <class 'node.tests.test_order.OrderReferenceSequenceNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
        ))

        # Detach subtree and insert elsewhere
        sub = tree1.detach('c')
        self.assertEqual(sub.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: c\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
        ))
        self.assertFalse(tree1._index is sub._index)
        self.assertTrue(sub._index is sub['d']._index is sub['e']._index)
        self.assertEqual(len(sub._index.keys()), 3)

        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: b\n"
        ))
        self.assertEqual(len(tree1._index.keys()), 3)

        sub.__name__ = 'x'
        tree1.insertbefore(sub, tree1['a'])
        self.assertEqual(tree1.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: None\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: x\n"
            "    <class 'node.tests.test_order.OrderReferenceSequenceNode'>: d\n"
            "    <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: a\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: b\n"
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
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
        ))

        tree2['d'].child_constraints = None
        tree2['d']['a'] = object()
        self.checkOutput("""\
        <class 'node.tests.test_order.OrderReferenceSequenceNode'>: x
        __<class 'node.tests.test_order.OrderReferenceSequenceNode'>: d
        ____a: <object object at ...>
        __<class 'node.tests.test_order.OrderReferenceSequenceNode'>: e
        """, tree2.treerepr(prefix='_'))

        tree2.detach('d')
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceSequenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceSequenceNode'>: e\n"
        ))

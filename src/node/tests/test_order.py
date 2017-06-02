from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors import Order
from node.behaviors import Reference
from node.tests import NodeTestCase
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Adopt,
    Order,
    DefaultInit,
    Nodify,
    OdictStorage)
class OrderableNode(object):
    pass


@plumbing(
    Adopt,
    Order,
    Reference,
    DefaultInit,
    Nodify,
    OdictStorage)
class OrderReferenceNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestOrder(NodeTestCase):

    ###########################################################################
    # Order without References
    ###########################################################################

    def test_insertion(self):
        # Node insertion. ``insertbefore`` and ``insertafter``
        node = OrderableNode('root')
        node['child1'] = OrderableNode()
        node['child2'] = OrderableNode()

        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

        new = OrderableNode()
        err = self.expect_error(
            ValueError,
            node.insertbefore,
            new,
            node['child1']
        )
        self.assertEqual(str(err), 'Given node has no __name__ set.')

        new.__name__ = 'child3'
        err = self.expect_error(
            ValueError,
            node.insertbefore,
            new,
            OrderableNode('fromelsewhere')
        )
        self.assertEqual(str(err), 'Given reference node not child of self.')

        node.insertbefore(new, node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

        new = OrderableNode(name='child4')
        node.insertafter(new, node['child3'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
        ))

        new = OrderableNode(name='child5')
        node.insertafter(new, node['child2'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child5\n"
        ))

        # Move a node. Therefor we first need to detach the node we want to
        # move from tree. Then insert the detached node elsewhere. In general,
        # you can insert the detached node or subtree to a complete different
        # tree
        detached = node.detach('child4')
        node.insertbefore(detached, node['child1'])
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child5\n"
        ))

        # Test ``insertfirst`` and ``insertlast``
        new = OrderableNode(name='first')
        node.insertfirst(new)
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: first\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child5\n"
        ))

        new = OrderableNode(name='last')
        node.insertlast(new)
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: first\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child4\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child1\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child3\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child2\n"
            "  <class 'node.tests.test_order.OrderableNode'>: child5\n"
            "  <class 'node.tests.test_order.OrderableNode'>: last\n"
        ))

        node.clear()
        new = OrderableNode(name='new')
        node.insertfirst(new)
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: new\n"
        ))

        node.clear()
        node.insertlast(new)
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_order.OrderableNode'>: root\n"
            "  <class 'node.tests.test_order.OrderableNode'>: new\n"
        ))

    def test_swap(self):
        # Test ``swap``
        node = OrderableNode('root')
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

    ###########################################################################
    # Order with References
    ###########################################################################

    def test_order_with_references(self):
        node = OrderReferenceNode(name='root')
        node['child1'] = OrderReferenceNode()
        node['child3'] = OrderReferenceNode()
        node['child4'] = OrderReferenceNode()
        node['child2'] = OrderReferenceNode()
        node['child5'] = OrderReferenceNode()

        err = self.expect_error(
            KeyError,
            node.insertbefore,
            node['child2'],
            node['child1']
        )
        self.assertEqual(str(err), "'Given node already contained in tree.'")

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

        err = self.expect_error(
            KeyError,
            tree1.insertbefore,
            sub,
            tree1['a']
        )
        self.assertEqual(str(err), "'Given node already contained in tree.'")

        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: d\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

        tree2['d'].allow_non_node_childs = True
        tree2['d']['a'] = object()
        self.check_output("""\
        <class 'node.tests.test_order.OrderReferenceNode'>: x
          <class 'node.tests.test_order.OrderReferenceNode'>: d
            a: <object object at ...>
          <class 'node.tests.test_order.OrderReferenceNode'>: e
        """, tree2.treerepr())

        tree2.detach('d')
        self.assertEqual(tree2.treerepr(), (
            "<class 'node.tests.test_order.OrderReferenceNode'>: x\n"
            "  <class 'node.tests.test_order.OrderReferenceNode'>: e\n"
        ))

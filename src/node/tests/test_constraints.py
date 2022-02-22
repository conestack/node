from node.base import BaseNode
from node.behaviors import DefaultInit
from node.behaviors import ListStorage
from node.behaviors import MappingConstraints
from node.behaviors import MappingNode
from node.behaviors import OdictStorage
from node.behaviors import SequenceConstraints
from node.behaviors import SequenceNode
from node.behaviors.constraints import check_constraints
from node.behaviors.constraints import child_constraints
from node.behaviors.constraints import Constraints
from node.interfaces import IMappingConstraints
from node.interfaces import INode
from node.tests import NodeTestCase
from plumber import plumbing


class TestConstraints(NodeTestCase):

    def test_child_constraints(self):
        class BC1:
            allow_non_node_childs = False

        ob = BC1()
        self.assertEqual(child_constraints(ob), (INode,))

        ob.allow_non_node_childs = True
        self.assertEqual(child_constraints(ob), tuple())

        class BC2:
            allow_non_node_children = False

        ob = BC2()
        self.assertEqual(child_constraints(ob), (INode,))

        ob.allow_non_node_children = True
        self.assertEqual(child_constraints(ob), tuple())

        class Constrains:
            child_constraints = None

        ob = Constrains()
        self.assertEqual(child_constraints(ob), tuple())

        ob.child_constraints = (int, float)
        self.assertEqual(child_constraints(ob), (int, float))

    def test_check_constraints(self):
        @plumbing(Constraints)
        class ConstraintsOb:
            pass

        self.assertEqual(ConstraintsOb.child_constraints, (INode,))

        ob = ConstraintsOb()
        self.assertEqual(check_constraints(ob, BaseNode()), None)

        with self.assertRaises(ValueError) as arc:
            check_constraints(ob, object())
        self.assertEqual(
            str(arc.exception),
            'Given value does not implement node.interfaces.INode'
        )

        ob.child_constraints = (int,)
        with self.assertRaises(ValueError) as arc:
            check_constraints(ob, '')
        self.assertEqual(
            str(arc.exception),
            'Given value is no instance of int'
        )
        self.assertEqual(check_constraints(ob, 0), None)

        ob.child_constraints = None
        self.assertEqual(check_constraints(ob, 0), None)

    def test_MappingConstraints(self):
        @plumbing(MappingConstraints, DefaultInit, MappingNode, OdictStorage)
        class MappingConstraintsNode(object):
            pass

        node = MappingConstraintsNode()
        with self.assertRaises(ValueError) as arc:
            node['child'] = 1
        self.assertEqual(
            str(arc.exception),
            'Given value does not implement node.interfaces.INode'
        )

        node.child_constraints = None
        node['child'] = 1
        self.assertEqual(node['child'], 1)

    def test_SequenceConstraints(self):
        @plumbing(SequenceConstraints, DefaultInit, SequenceNode, ListStorage)
        class SequenceConstraintsNode(object):
            pass

        node = SequenceConstraintsNode()
        with self.assertRaises(ValueError) as arc:
            node.insert(0, 1)
        self.assertEqual(
            str(arc.exception),
            'Given value does not implement node.interfaces.INode'
        )
        with self.assertRaises(ValueError) as arc:
            node['0'] = 1
        self.assertEqual(
            str(arc.exception),
            'Given value does not implement node.interfaces.INode'
        )

        node.child_constraints = None
        node.insert(0, 1)
        self.assertEqual(node['0'], 1)
        node['0'] = 0
        self.assertEqual(node['0'], 0)

    def test_BC_imports(self):
        from node.behaviors import NodeChildValidate
        self.assertTrue(MappingConstraints is NodeChildValidate)

        from node.interfaces import INodeChildValidate
        self.assertTrue(IMappingConstraints is INodeChildValidate)

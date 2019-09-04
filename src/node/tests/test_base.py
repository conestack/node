from node.base import AbstractNode
from node.base import BaseNode
from node.base import OrderedNode
from node.testing import FullMappingTester
from node.testing.base import create_tree
from node.testing.env import MyNode
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import noLongerProvides
import copy
import pickle


class TestBase(NodeTestCase):

    def test_AbstractNode(self):
        self.assertEqual(AbstractNode.__bases__, (object,))
        abstract = AbstractNode()
        self.assertTrue(
            str(abstract).startswith('<AbstractNode object \'None\' at')
        )

        # Storage related operations of ``AbstractNode`` raises
        # ``NotImplementedError``:

        def __getitem__fails():
            abstract['foo']
        self.expectError(NotImplementedError, __getitem__fails)

        def __delitem__fails():
            del abstract['foo']
        self.expectError(NotImplementedError, __delitem__fails)

        def __setitem__fails():
            abstract['foo'] = 'bar'
        self.expectError(NotImplementedError, __setitem__fails)

        def __iter__fails():
            [key for key in abstract]
        self.expectError(NotImplementedError, __iter__fails)

        def clear_fails():
            abstract.clear()
        self.expectError(NotImplementedError, clear_fails)

        def update_fails():
            abstract.update((('foo', 'bar'),))
        self.expectError(NotImplementedError, update_fails)

        def setdefaut_fails():
            abstract.setdefault('foo', 'bar')
        self.expectError(NotImplementedError, setdefaut_fails)

        def pop_fails():
            abstract.pop('foo')
        self.expectError(NotImplementedError, pop_fails)

        def popitem_fails():
            abstract.popitem()
        self.expectError(NotImplementedError, popitem_fails)

    def test_MyNode(self):
        # ``node.testing.env`` contains a base node implementation inheriting
        # from ``AbstractNode`` for illustration purposes:
        mynode = MyNode()
        self.assertTrue(
            str(mynode).startswith('<MyNode object \'None\' at')
        )
        fmtester = FullMappingTester(MyNode)
        fmtester.run()
        self.checkOutput("""\
        ``__contains__``: OK
        ``__delitem__``: OK
        ``__getitem__``: OK
        ``__iter__``: OK
        ``__len__``: OK
        ``__setitem__``: OK
        ``clear``: OK
        ``copy``: OK
        ``get``: OK
        ``has_key``: OK
        ``items``: OK
        ``iteritems``: OK
        ``iterkeys``: OK
        ``itervalues``: OK
        ``keys``: OK
        ``pop``: OK
        ``popitem``: OK
        ``setdefault``: OK
        ``update``: OK
        ``values``: OK
        """, fmtester.combined)

    def test_BaseNode(self):
        self.assertEqual(BaseNode.__bases__, (object,))
        basenode = BaseNode()
        self.assertTrue(
            str(basenode).startswith('<BaseNode object \'None\' at')
        )
        fmtester = FullMappingTester(BaseNode)
        fmtester.run()
        self.checkOutput("""\
        ``__contains__``: OK
        ``__delitem__``: OK
        ``__getitem__``: OK
        ``__iter__``: OK
        ``__len__``: OK
        ``__setitem__``: OK
        ``clear``: OK
        ``copy``: OK
        ``get``: OK
        ``has_key``: OK
        ``items``: OK
        ``iteritems``: OK
        ``iterkeys``: OK
        ``itervalues``: OK
        ``keys``: OK
        ``pop``: OK
        ``popitem``: OK
        ``setdefault``: OK
        ``update``: OK
        ``values``: OK
        """, fmtester.combined)

    def test_OrderedNode(self):
        self.assertEqual(OrderedNode.__bases__, (object,))
        orderednode = OrderedNode()
        self.assertTrue(
            str(orderednode).startswith('<OrderedNode object \'None\' at')
        )
        fmtester = FullMappingTester(OrderedNode)
        fmtester.run()
        self.checkOutput("""\
        ``__contains__``: OK
        ``__delitem__``: OK
        ``__getitem__``: OK
        ``__iter__``: OK
        ``__len__``: OK
        ``__setitem__``: OK
        ``clear``: OK
        ``copy``: OK
        ``get``: OK
        ``has_key``: OK
        ``items``: OK
        ``iteritems``: OK
        ``iterkeys``: OK
        ``itervalues``: OK
        ``keys``: OK
        ``pop``: OK
        ``popitem``: OK
        ``setdefault``: OK
        ``update``: OK
        ``values``: OK
        """, fmtester.combined)

        orderednode['child'] = OrderedNode()
        self.checkOutput("""\
        <class 'node.base.OrderedNode'>: None
        __<class 'node.base.OrderedNode'>: child
        """, orderednode.treerepr(prefix='_'))

        unpickled = pickle.loads(pickle.dumps(orderednode))
        self.checkOutput("""\
        <class 'node.base.OrderedNode'>: None
        __<class 'node.base.OrderedNode'>: child
        """, unpickled.treerepr(prefix='_'))

    def test_ILocation(self):
        # XXX: make tester object for ``ILocation`` contract.

        # ``ILocations`` promises ``__name__`` and ``__parent__`` attributes.
        # They are used to define tree hierarchy. As read only arguments they
        # are available at ``name`` and ``parent`` on nodes:
        mynode = create_tree(MyNode)
        self.assertTrue(
            str(mynode).startswith('<MyNode object \'None\' at')
        )
        self.assertEqual(mynode.__name__, None)
        self.assertEqual(mynode.__parent__, None)
        self.assertEqual(mynode.name, None)
        self.assertEqual(mynode.parent, None)
        self.assertEqual(mynode['child_1'].name, 'child_1')
        self.assertTrue(mynode['child_1'].parent is mynode)
        self.assertEqual(mynode['child_1']['subchild_1'].name, 'subchild_1')
        self.assertTrue(
            mynode['child_1']['subchild_1'].parent.parent is mynode
        )

        basenode = create_tree(BaseNode)
        self.assertTrue(
            str(basenode).startswith('<BaseNode object \'None\' at')
        )
        self.assertEqual(basenode.name, None)
        self.assertEqual(basenode.parent, None)
        self.assertEqual(basenode['child_1'].name, 'child_1')
        self.assertTrue(basenode['child_1'].parent is basenode)
        self.assertEqual(basenode['child_1']['subchild_1'].name, 'subchild_1')
        self.assertTrue(
            basenode['child_1']['subchild_1'].parent.parent is basenode
        )

        orderednode = create_tree(OrderedNode)
        self.assertTrue(
            str(orderednode).startswith('<OrderedNode object \'None\' at')
        )
        self.assertEqual(orderednode.name, None)
        self.assertEqual(orderednode.parent, None)
        self.assertEqual(orderednode['child_1'].name, 'child_1')
        self.assertTrue(orderednode['child_1'].parent is orderednode)
        self.assertEqual(
            orderednode['child_1']['subchild_1'].name, 'subchild_1'
        )
        self.assertTrue(
            orderednode['child_1']['subchild_1'].parent.parent is orderednode
        )

    def test_INode(self):
        # XXX: make tester object for INode contract
        # XXX: decide wether ``aliases`` or ``aliaser`` (still dunno) should be
        #      kept in base interface.

        # printtree
        mynode = create_tree(MyNode)
        self.checkOutput("""\
        <class 'node.testing.env.MyNode'>: None
        __<class 'node.testing.env.MyNode'>: child_0
        ____<class 'node.testing.env.MyNode'>: subchild_0
        ____<class 'node.testing.env.MyNode'>: subchild_1
        __<class 'node.testing.env.MyNode'>: child_1
        ____<class 'node.testing.env.MyNode'>: subchild_0
        ____<class 'node.testing.env.MyNode'>: subchild_1
        __<class 'node.testing.env.MyNode'>: child_2
        ____<class 'node.testing.env.MyNode'>: subchild_0
        ____<class 'node.testing.env.MyNode'>: subchild_1
        """, mynode.treerepr(prefix='_'))

        basenode = create_tree(BaseNode)
        self.checkOutput("""\
        <class 'node.base.BaseNode'>: None
        __<class 'node.base.BaseNode'>: child_...
        ____<class 'node.base.BaseNode'>: subchild_...
        ____<class 'node.base.BaseNode'>: subchild_...
        __<class 'node.base.BaseNode'>: child_...
        ____<class 'node.base.BaseNode'>: subchild_...
        ____<class 'node.base.BaseNode'>: subchild_...
        __<class 'node.base.BaseNode'>: child_...
        ____<class 'node.base.BaseNode'>: subchild_...
        ____<class 'node.base.BaseNode'>: subchild_...
        """, basenode.treerepr(prefix='_'))

        orderednode = create_tree(OrderedNode)
        self.checkOutput("""\
        <class 'node.base.OrderedNode'>: None
        __<class 'node.base.OrderedNode'>: child_0
        ____<class 'node.base.OrderedNode'>: subchild_0
        ____<class 'node.base.OrderedNode'>: subchild_1
        __<class 'node.base.OrderedNode'>: child_1
        ____<class 'node.base.OrderedNode'>: subchild_0
        ____<class 'node.base.OrderedNode'>: subchild_1
        __<class 'node.base.OrderedNode'>: child_2
        ____<class 'node.base.OrderedNode'>: subchild_0
        ____<class 'node.base.OrderedNode'>: subchild_1
        """, orderednode.treerepr(prefix='_'))

        # path
        mynode.__name__ = 'root'
        self.assertEqual(mynode.path, ['root'])
        self.assertEqual(
            mynode['child_1']['subchild_1'].path,
            ['root', 'child_1', 'subchild_1']
        )

        basenode.__name__ = 'root'
        self.assertEqual(basenode.path, ['root'])
        self.assertEqual(
            basenode['child_1']['subchild_1'].path,
            ['root', 'child_1', 'subchild_1']
        )

        orderednode.__name__ = 'root'
        self.assertEqual(orderednode.path, ['root'])
        self.assertEqual(
            orderednode['child_1']['subchild_1'].path,
            ['root', 'child_1', 'subchild_1']
        )

        # root
        self.assertTrue(mynode['child_1']['subchild_1'].root is mynode)
        self.assertTrue(basenode['child_1']['subchild_1'].root is basenode)
        self.assertTrue(
            orderednode['child_1']['subchild_1'].root is orderednode
        )

        # allow_non_node_childs
        self.assertFalse(mynode.allow_non_node_childs)

        def non_node_childs_not_allowed():
            mynode['foo'] = object()
        err = self.expectError(ValueError, non_node_childs_not_allowed)
        self.assertEqual(str(err), 'Non-node childs are not allowed.')

        def no_classes_as_values_allowed():
            mynode['foo'] = object
        err = self.expectError(ValueError, no_classes_as_values_allowed)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

        mynode.allow_non_node_childs = True
        obj = mynode['foo'] = object()
        self.assertEqual(mynode['foo'], obj)

        del mynode['foo']
        mynode.allow_non_node_childs = False

        self.assertFalse(basenode.allow_non_node_childs)

        def non_node_childs_not_allowed2():
            basenode['foo'] = object()
        err = self.expectError(ValueError, non_node_childs_not_allowed2)
        self.assertEqual(str(err), 'Non-node childs are not allowed.')

        def no_classes_as_values_allowed2():
            basenode['foo'] = object
        err = self.expectError(ValueError, no_classes_as_values_allowed2)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

        basenode.allow_non_node_childs = True
        obj = basenode['foo'] = object()
        self.assertEqual(basenode['foo'], obj)

        del basenode['foo']
        basenode.allow_non_node_childs = False

        self.assertFalse(orderednode.allow_non_node_childs)

        def non_node_childs_not_allowed3():
            orderednode['foo'] = object()
        err = self.expectError(ValueError, non_node_childs_not_allowed3)
        self.assertEqual(str(err), 'Non-node childs are not allowed.')

        def no_classes_as_values_allowed3():
            orderednode['foo'] = object
        err = self.expectError(ValueError, no_classes_as_values_allowed3)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

        orderednode.allow_non_node_childs = True
        obj = orderednode['foo'] = object()
        self.assertEqual(orderednode['foo'], obj)

        del orderednode['foo']
        orderednode.allow_non_node_childs = False

        # filteredvalues and filtereditervalues
        class IFilter(Interface):
            pass

        directlyProvides(mynode['child_2'], IFilter)
        self.assertEqual(
            list(mynode.filtereditervalues(IFilter)),
            [mynode['child_2']]
        )
        self.assertEqual(
            mynode.filteredvalues(IFilter),
            [mynode['child_2']]
        )
        noLongerProvides(mynode['child_2'], IFilter)
        self.assertEqual(list(mynode.filtereditervalues(IFilter)), [])
        self.assertEqual(mynode.filteredvalues(IFilter), [])

        directlyProvides(basenode['child_2'], IFilter)
        self.assertEqual(
            list(basenode.filtereditervalues(IFilter)),
            [basenode['child_2']]
        )
        self.assertEqual(
            basenode.filteredvalues(IFilter),
            [basenode['child_2']]
        )
        noLongerProvides(basenode['child_2'], IFilter)
        self.assertEqual(list(basenode.filtereditervalues(IFilter)), [])
        self.assertEqual(basenode.filteredvalues(IFilter), [])

        directlyProvides(orderednode['child_2'], IFilter)
        self.assertEqual(
            list(orderednode.filtereditervalues(IFilter)),
            [orderednode['child_2']]
        )
        self.assertEqual(
            orderednode.filteredvalues(IFilter),
            [orderednode['child_2']]
        )
        noLongerProvides(orderednode['child_2'], IFilter)
        self.assertEqual(list(orderednode.filtereditervalues(IFilter)), [])
        self.assertEqual(orderednode.filteredvalues(IFilter), [])

        # as_attribute_access
        myattrs = mynode.as_attribute_access()
        self.assertEqual(myattrs.__class__, AttributeAccess)
        self.assertEqual(myattrs.child_1, mynode['child_1'])
        myattrs.child_3 = MyNode()
        self.assertEqual(mynode['child_3'], myattrs.child_3)

        def no_classes_as_values_allowed4():
            myattrs.child_4 = object
        err = self.expectError(ValueError, no_classes_as_values_allowed4)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

        baseattrs = basenode.as_attribute_access()
        self.assertEqual(baseattrs.__class__, AttributeAccess)
        self.assertEqual(baseattrs.child_1, basenode['child_1'])
        baseattrs.child_3 = BaseNode()
        self.assertEqual(basenode['child_3'], baseattrs.child_3)

        def no_classes_as_values_allowed5():
            baseattrs.child_4 = object
        err = self.expectError(ValueError, no_classes_as_values_allowed5)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

        orderedattrs = orderednode.as_attribute_access()
        self.assertEqual(orderedattrs.__class__, AttributeAccess)
        self.assertEqual(orderedattrs.child_1, orderednode['child_1'])
        orderedattrs.child_3 = OrderedNode()
        self.assertEqual(orderednode['child_3'], orderedattrs.child_3)

        def no_classes_as_values_allowed6():
            orderedattrs.child_4 = object
        err = self.expectError(ValueError, no_classes_as_values_allowed6)
        expected = 'It isn\'t allowed to use classes as values.'
        self.assertEqual(str(err), expected)

    def test_copy(self):
        node = BaseNode()
        node['child'] = BaseNode()

        # Shallow copy of BaseNode
        copied_node = node.copy()
        self.checkOutput("""\
        <class 'node.base.BaseNode'>: None
        __<class 'node.base.BaseNode'>: child
        """, copied_node.treerepr(prefix='_'))

        self.assertFalse(node is copied_node)
        self.assertTrue(node['child'] is copied_node['child'])

        copied_node = copy.copy(node)
        self.assertFalse(node is copied_node)
        self.assertTrue(node['child'] is copied_node['child'])

        # Deep copy of base node
        copied_node = node.deepcopy()
        self.checkOutput("""\
        <class 'node.base.BaseNode'>: None
        __<class 'node.base.BaseNode'>: child
        """, copied_node.treerepr(prefix='_'))

        self.assertFalse(node is copied_node)
        self.assertFalse(node['child'] is copied_node['child'])

        copied_node = copy.deepcopy(node)
        self.assertFalse(node is copied_node)
        self.assertFalse(node['child'] is copied_node['child'])

        # Shallow copy of ordered node
        node = OrderedNode()
        node['child'] = OrderedNode()

        copied_node = node.copy()
        self.checkOutput("""\
        <class 'node.base.OrderedNode'>: None
        __<class 'node.base.OrderedNode'>: child
        """, copied_node.treerepr(prefix='_'))

        self.assertFalse(node is copied_node)
        self.assertTrue(node['child'] is copied_node['child'])

        copied_node = copy.copy(node)
        self.assertFalse(node is copied_node)
        self.assertTrue(node['child'] is copied_node['child'])

        # Deep copy of ordered node
        node = OrderedNode()
        node['child'] = OrderedNode()

        copied_node = node.deepcopy()
        self.checkOutput("""\
        <class 'node.base.OrderedNode'>: None
        __<class 'node.base.OrderedNode'>: child
        """, copied_node.treerepr(prefix='_'))

        self.assertFalse(node is copied_node)
        self.assertFalse(node['child'] is copied_node['child'])

        copied_node = copy.deepcopy(node)
        self.assertFalse(node is copied_node)
        self.assertFalse(node['child'] is copied_node['child'])

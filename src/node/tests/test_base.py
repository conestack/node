from node.base import AbstractNode
from node.base import BaseNode
from node.base import OrderedNode
from node.testing import FullMappingTester
from node.testing.env import MyNode
from node.tests import NodeTestCase
from node.testing.base import create_tree
import pickle


class TestBase(NodeTestCase):

    def test_AbstractNode(self):
        self.assertEquals(AbstractNode.__bases__, (object,))
        abstract = AbstractNode()
        self.assertTrue(
            str(abstract).startswith('<AbstractNode object \'None\' at')
        )

        # Storage related operations of ``AbstractNode`` raises
        # ``NotImplementedError``:

        def __getitem__fails():
            abstract['foo']
        self.except_error(NotImplementedError, __getitem__fails)

        def __delitem__fails():
            del abstract['foo']
        self.except_error(NotImplementedError, __delitem__fails)

        def __setitem__fails():
            abstract['foo'] = 'bar'
        self.except_error(NotImplementedError, __setitem__fails)

        def __iter__fails():
            [key for key in abstract]
        self.except_error(NotImplementedError, __iter__fails)

        def clear_fails():
            abstract.clear()
        self.except_error(NotImplementedError, clear_fails)

        def update_fails():
            abstract.update((('foo', 'bar'),))
        self.except_error(NotImplementedError, update_fails)

        def setdefaut_fails():
            abstract.setdefault('foo', 'bar')
        self.except_error(NotImplementedError, setdefaut_fails)

        def pop_fails():
            abstract.pop('foo')
        self.except_error(NotImplementedError, pop_fails)

        def popitem_fails():
            abstract.popitem()
        self.except_error(NotImplementedError, popitem_fails)

    def test_MyNode(self):
        # ``node.testing.env`` contains a base node implementation inheriting
        # from ``AbstractNode`` for illustration purposes:
        mynode = MyNode()
        self.assertTrue(
            str(mynode).startswith('<MyNode object \'None\' at')
        )
        fmtester = FullMappingTester(MyNode)
        fmtester.run()
        self.check_output("""\
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
        self.assertEquals(BaseNode.__bases__, (object,))
        basenode = BaseNode()
        self.assertTrue(
            str(basenode).startswith('<BaseNode object \'None\' at')
        )
        fmtester = FullMappingTester(BaseNode)
        fmtester.run()
        self.check_output("""\
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
        self.assertEquals(OrderedNode.__bases__, (object,))
        orderednode = OrderedNode()
        self.assertTrue(
            str(orderednode).startswith('<OrderedNode object \'None\' at')
        )
        fmtester = FullMappingTester(OrderedNode)
        fmtester.run()
        self.check_output("""\
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
        self.check_output("""\
        <class 'node.base.OrderedNode'>: None
          <class 'node.base.OrderedNode'>: child
        """, orderednode.treerepr())

        unpickled = pickle.loads(pickle.dumps(orderednode))
        self.check_output("""\
        <class 'node.base.OrderedNode'>: None
          <class 'node.base.OrderedNode'>: child
        """, unpickled.treerepr())

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
        self.check_output("""\
        <class 'node.testing.env.MyNode'>: None
          <class 'node.testing.env.MyNode'>: child_0
            <class 'node.testing.env.MyNode'>: subchild_0
            <class 'node.testing.env.MyNode'>: subchild_1
          <class 'node.testing.env.MyNode'>: child_1
            <class 'node.testing.env.MyNode'>: subchild_0
            <class 'node.testing.env.MyNode'>: subchild_1
          <class 'node.testing.env.MyNode'>: child_2
            <class 'node.testing.env.MyNode'>: subchild_0
            <class 'node.testing.env.MyNode'>: subchild_1
        """, mynode.treerepr())

        basenode = create_tree(BaseNode)
        self.check_output("""\
        <class 'node.base.BaseNode'>: None
          <class 'node.base.BaseNode'>: child_...
            <class 'node.base.BaseNode'>: subchild_...
            <class 'node.base.BaseNode'>: subchild_...
          <class 'node.base.BaseNode'>: child_...
            <class 'node.base.BaseNode'>: subchild_...
            <class 'node.base.BaseNode'>: subchild_...
          <class 'node.base.BaseNode'>: child_...
            <class 'node.base.BaseNode'>: subchild_...
            <class 'node.base.BaseNode'>: subchild_...
        """, basenode.treerepr())

        orderednode = create_tree(OrderedNode)
        self.check_output("""\
        <class 'node.base.OrderedNode'>: None
          <class 'node.base.OrderedNode'>: child_0
            <class 'node.base.OrderedNode'>: subchild_0
            <class 'node.base.OrderedNode'>: subchild_1
          <class 'node.base.OrderedNode'>: child_1
            <class 'node.base.OrderedNode'>: subchild_0
            <class 'node.base.OrderedNode'>: subchild_1
          <class 'node.base.OrderedNode'>: child_2
            <class 'node.base.OrderedNode'>: subchild_0
            <class 'node.base.OrderedNode'>: subchild_1
        """, orderednode.treerepr())

"""

path
~~~~

.. code-block:: pycon

    >>> mynode.__name__ = 'root'
    >>> mynode.path
    ['root']

    >>> mynode['child_1']['subchild_1'].path
    ['root', 'child_1', 'subchild_1']

    >>> basenode.__name__ = 'root'
    >>> basenode.path
    ['root']

    >>> basenode['child_1']['subchild_1'].path
    ['root', 'child_1', 'subchild_1']

    >>> orderednode.__name__ = 'root'
    >>> orderednode.path
    ['root']

    >>> orderednode['child_1']['subchild_1'].path
    ['root', 'child_1', 'subchild_1']


root
~~~~

.. code-block:: pycon

    >>> mynode['child_1']['subchild_1'].root is mynode
    True

    >>> basenode['child_1']['subchild_1'].root is basenode
    True

    >>> orderednode['child_1']['subchild_1'].root is orderednode
    True


allow_non_node_childs
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: pycon

    >>> mynode.allow_non_node_childs
    False

    >>> mynode['foo'] = object()
    Traceback (most recent call last):
      ...
    ValueError: Non-node childs are not allowed.

    >>> mynode['foo'] = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> mynode.allow_non_node_childs = True
    >>> mynode['foo'] = object()
    >>> mynode['foo']
    <object object at ...>

    >>> del mynode['foo']
    >>> mynode.allow_non_node_childs = False

    >>> basenode.allow_non_node_childs
    False

    >>> basenode['foo'] = object()
    Traceback (most recent call last):
      ...
    ValueError: Non-node childs are not allowed.

    >>> basenode['foo'] = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> basenode.allow_non_node_childs = True
    >>> basenode['foo'] = object()
    >>> basenode['foo']
    <object object at ...>

    >>> del basenode['foo']
    >>> basenode.allow_non_node_childs = False

    >>> orderednode.allow_non_node_childs
    False

    >>> orderednode['foo'] = object()
    Traceback (most recent call last):
      ...
    ValueError: Non-node childs are not allowed.

    >>> orderednode['foo'] = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> orderednode.allow_non_node_childs = True
    >>> orderednode['foo'] = object()
    >>> orderednode['foo']
    <object object at ...>

    >>> del orderednode['foo']
    >>> orderednode.allow_non_node_childs = False


filteredvalues
~~~~~~~~~~~~~~

.. code-block:: pycon

    >>> from zope.interface import Interface
    >>> from zope.interface import directlyProvides
    >>> from zope.interface import noLongerProvides

    >>> class IFilter(Interface):
    ...     pass

    >>> directlyProvides(mynode['child_2'], IFilter)
    >>> list(mynode.filtereditervalues(IFilter))
    [<MyNode object 'child_2' at ...>]

    >>> mynode.filteredvalues(IFilter)
    [<MyNode object 'child_2' at ...>]

    >>> noLongerProvides(mynode['child_2'], IFilter)
    >>> list(mynode.filtereditervalues(IFilter))
    []

    >>> mynode.filteredvalues(IFilter)
    []

    >>> directlyProvides(basenode['child_2'], IFilter)
    >>> list(basenode.filtereditervalues(IFilter))
    [<BaseNode object 'child_2' at ...>]

    >>> basenode.filteredvalues(IFilter)
    [<BaseNode object 'child_2' at ...>]

    >>> noLongerProvides(basenode['child_2'], IFilter)
    >>> list(basenode.filtereditervalues(IFilter))
    []

    >>> basenode.filteredvalues(IFilter)
    []

    >>> directlyProvides(orderednode['child_2'], IFilter)
    >>> list(orderednode.filtereditervalues(IFilter))
    [<OrderedNode object 'child_2' at ...>]

    >>> orderednode.filteredvalues(IFilter)
    [<OrderedNode object 'child_2' at ...>]

    >>> noLongerProvides(orderednode['child_2'], IFilter)
    >>> list(orderednode.filtereditervalues(IFilter))
    []

    >>> orderednode.filteredvalues(IFilter)
    []


as_attribute_access
~~~~~~~~~~~~~~~~~~~

.. code-block:: pycon

    >>> myattrs = mynode.as_attribute_access()
    >>> myattrs
    <node.utils.AttributeAccess object at ...>

    >>> myattrs.child_1
    <MyNode object 'child_1' at ...>

    >>> myattrs.child_3 = MyNode()
    >>> mynode['child_3']
    <MyNode object 'child_3' at ...>

    >>> myattrs.child_4 = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> baseattrs = basenode.as_attribute_access()
    >>> baseattrs
    <node.utils.AttributeAccess object at ...>

    >>> baseattrs.child_1
    <BaseNode object 'child_1' at ...>

    >>> baseattrs.child_3 = BaseNode()
    >>> basenode['child_3']
    <BaseNode object 'child_3' at ...>

    >>> baseattrs.child_4 = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> orderedattrs = orderednode.as_attribute_access()
    >>> orderedattrs
    <node.utils.AttributeAccess object at ...>

    >>> orderedattrs.child_1
    <OrderedNode object 'child_1' at ...>

    >>> orderedattrs.child_3 = OrderedNode()
    >>> orderednode['child_3']
    <OrderedNode object 'child_3' at ...>

    >>> orderedattrs.child_4 = object
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.


Copy testing
============

Shallow copy of BaseNode:

.. code-block:: pycon

    >>> import copy
    >>> node = BaseNode()
    >>> node['child'] = BaseNode()

    >>> copied_node = node.copy()
    >>> copied_node.printtree()
    <class 'node.base.BaseNode'>: None
      <class 'node.base.BaseNode'>: child

    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    True

    >>> copied_node = copy.copy(node)
    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    True

Deep copy of base node:

.. code-block:: pycon

    >>> copied_node = node.deepcopy()
    >>> copied_node.printtree()
    <class 'node.base.BaseNode'>: None
      <class 'node.base.BaseNode'>: child

    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    False

    >>> copied_node = copy.deepcopy(node)
    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    False

Shallow copy of ordered node:

.. code-block:: pycon

    >>> node = OrderedNode()
    >>> node['child'] = OrderedNode()

    >>> copied_node = node.copy()
    >>> copied_node.printtree()
    <class 'node.base.OrderedNode'>: None
      <class 'node.base.OrderedNode'>: child

    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    True

    >>> copied_node = copy.copy(node)
    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    True

Deep copy of ordered node:

.. code-block:: pycon

    >>> node = OrderedNode()
    >>> node['child'] = OrderedNode()

    >>> copied_node = node.deepcopy()
    >>> copied_node.printtree()
    <class 'node.base.OrderedNode'>: None
      <class 'node.base.OrderedNode'>: child

    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    False

    >>> copied_node = copy.deepcopy(node)
    >>> node is copied_node
    False

    >>> node['child'] is copied_node['child']
    False

"""
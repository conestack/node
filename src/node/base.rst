node.base
=========

::
    >>> from node.testing import FullMappingTester


AbstractNode
------------

::
    >>> from node.base import AbstractNode
    >>> AbstractNode
    <class 'node.base.AbstractNode'>
    
    >>> AbstractNode.__bases__
    (<type 'object'>,)
    
    >>> abstract = AbstractNode()
    >>> abstract
    <AbstractNode object 'None' at ...>

Storage related operations of AbstractNode raise ``NotImplementedError``::

    >>> abstract['foo']
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> del abstract['foo']
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract['foo'] = 'bar'
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> [key for key in abstract]
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract.clear()
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract.update((('foo', 'bar'),))
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract.setdefault('foo', 'bar')
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract.pop('foo')
    Traceback (most recent call last):
      ...
    NotImplementedError
    
    >>> abstract.popitem()
    Traceback (most recent call last):
      ...
    NotImplementedError
    
``node.testing.env`` contains a base node implementation inheriting from
``AbstractNode`` for illustration purposes::

    >>> from node.testing.env import MyNode
    >>> mynode = MyNode()
    >>> mynode
    <MyNode object 'None' at ...>
    
    >>> tester = FullMappingTester(MyNode)
    >>> tester.run()
    >>> tester.combined
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


BaseNode
--------
::
    >>> from node.base import BaseNode
    >>> BaseNode
    <class 'node.base.BaseNode'>
    
    >>> BaseNode.__bases__
    (<type 'object'>,)
    
    >>> basenode = BaseNode()
    >>> basenode
    <BaseNode object 'None' at ...>
    
    >>> tester = FullMappingTester(BaseNode)
    >>> tester.run()
    >>> tester.combined
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

OrderedNode
-----------
::
    >>> from node.base import OrderedNode
    >>> OrderedNode
    <class 'node.base.OrderedNode'>
    
    >>> OrderedNode.__bases__
    (<type 'object'>,)
    
    >>> orderednode = OrderedNode()
    >>> orderednode
    <OrderedNode object 'None' at ...>
    
    >>> tester = FullMappingTester(OrderedNode)
    >>> tester.run()
    >>> tester.combined
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
    
    >>> orderednode['child'] = OrderedNode()
    >>> orderednode.printtree()
    <class 'node.base.OrderedNode'>: None
      <class 'node.base.OrderedNode'>: child
    
    >>> import pickle
    >>> unpickled = pickle.loads(pickle.dumps(orderednode))
    >>> unpickled.printtree()
    <class 'node.base.OrderedNode'>: None
      <class 'node.base.OrderedNode'>: child


ILocation contract
------------------

XXX: make tester object for ILocation contract

``ILocations`` promises ``__name__`` and ``__parent__`` attributes. They are
used to define tree hierarchy. As read only arguments they are available
at ``name`` and ``parent`` on nodes::

    >>> from node.testing.base import create_tree
    >>> mynode = create_tree(MyNode)
    >>> mynode
    <MyNode object 'None' at ...>
    
    >>> mynode.__name__
    >>> mynode.__parent__
    
    >>> mynode.name
    >>> mynode.parent
    
    >>> mynode['child_1'].name
    'child_1'
    
    >>> mynode['child_1'].parent is mynode
    True
    
    >>> mynode['child_1']['subchild_1'].name
    'subchild_1'
    
    >>> mynode['child_1']['subchild_1'].parent.parent is mynode
    True
    
    >>> basenode = create_tree(BaseNode)
    >>> basenode
    <BaseNode object 'None' at ...>
    
    >>> basenode.name
    >>> basenode.parent
    
    >>> basenode['child_1'].name
    'child_1'
    
    >>> basenode['child_1'].parent is basenode
    True
    
    >>> basenode['child_1']['subchild_1'].name
    'subchild_1'
    
    >>> basenode['child_1']['subchild_1'].parent.parent is basenode
    True
    
    >>> orderednode = create_tree(OrderedNode)
    >>> orderednode
    <OrderedNode object 'None' at ...>

    >>> orderednode.name
    >>> orderednode.parent
    
    >>> orderednode['child_1'].name
    'child_1'
    
    >>> orderednode['child_1'].parent is orderednode
    True
    
    >>> orderednode['child_1']['subchild_1'].name
    'subchild_1'
    
    >>> orderednode['child_1']['subchild_1'].parent.parent is orderednode
    True


INode contract
--------------

XXX: make tester object for INode contract

XXX: decide wether ``aliases`` or ``aliaser`` (still dunno) should be kept in
     base interface.

``printtree``::

    >>> mynode.printtree()
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
    
    >>> basenode.printtree()
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
    
    >>> orderednode.printtree()
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

``path``::

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

``root``::

    >>> mynode['child_1']['subchild_1'].root is mynode
    True
    
    >>> basenode['child_1']['subchild_1'].root is basenode
    True
    
    >>> orderednode['child_1']['subchild_1'].root is orderednode
    True

``allow_non_node_childs``::

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

``filteredvalues``::

    >>> from zope.interface import Interface, directlyProvides, noLongerProvides
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

``as_attribute_access``::

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

Shallow copy of BaseNode::
    
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

Deep copy of base node::

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

Shallow copy of ordered node::

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
    
Deep copy of ordered node::

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
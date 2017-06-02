Order
=====

Order without References
------------------------

Node insertion. ``insertbefore`` and ``insertafter``:

.. code-block:: pycon

    >>> from plumber import plumbing
    >>> from node.behaviors import Adopt
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from node.behaviors import Order
    >>> from node.behaviors import Reference

    >>> @plumbing(
    ...     Adopt,
    ...     Order,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class OrderableNode(object):
    ...     pass

    >>> node = OrderableNode('root')

    >>> node['child1'] = OrderableNode()
    >>> node['child2'] = OrderableNode()
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child2

    >>> new = OrderableNode()
    >>> node.insertbefore(new, node['child1'])
    Traceback (most recent call last):
      ...
    ValueError: Given node has no __name__ set.

    >>> new.__name__ = 'child3'
    >>> node.insertbefore(new, OrderableNode('fromelsewhere'))
    Traceback (most recent call last):
      ...
    ValueError: Given reference node not child of self.

    >>> node.insertbefore(new, node['child2'])
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child2

    >>> new = OrderableNode(name='child4')
    >>> node.insertafter(new, node['child3'])
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child4
      <class 'OrderableNode'>: child2

    >>> new = OrderableNode(name='child5')
    >>> node.insertafter(new, node['child2'])
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child4
      <class 'OrderableNode'>: child2
      <class 'OrderableNode'>: child5

Move a node. Therefor we first need to detach the node we want to move from
tree. Then insert the detached node elsewhere. In general, you can insert the
detached node or subtree to a complete different tree:

.. code-block:: pycon

    >>> detached = node.detach('child4')
    >>> node.insertbefore(detached, node['child1'])
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: child4
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child2
      <class 'OrderableNode'>: child5

Test ``insertfirst`` and ``insertlast``:

.. code-block:: pycon

    >>> new = OrderableNode(name='first')
    >>> node.insertfirst(new)
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: first
      <class 'OrderableNode'>: child4
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child2
      <class 'OrderableNode'>: child5

    >>> new = OrderableNode(name='last')
    >>> node.insertlast(new)
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: first
      <class 'OrderableNode'>: child4
      <class 'OrderableNode'>: child1
      <class 'OrderableNode'>: child3
      <class 'OrderableNode'>: child2
      <class 'OrderableNode'>: child5
      <class 'OrderableNode'>: last

    >>> node.clear()
    >>> new = OrderableNode(name='new')
    >>> node.insertfirst(new)
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: new

    >>> node.clear()
    >>> node.insertlast(new)
    >>> node.printtree()
    <class 'OrderableNode'>: root
      <class 'OrderableNode'>: new

Test ``swap``:

.. code-block:: pycon

    >>> node.clear()
    >>> node['0'] = OrderableNode()
    >>> node['1'] = OrderableNode()
    >>> node['2'] = OrderableNode()
    >>> node['3'] = OrderableNode()
    >>> node['4'] = OrderableNode()
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case first 2, a < b:

.. code-block:: pycon

    >>> node.swap(node['0'], node['1'])
    >>> node.keys()
    ['1', '0', '2', '3', '4']

Case first 2, a > b:

.. code-block:: pycon

    >>> node.swap(node['0'], node['1'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case last 2, a < b:

.. code-block:: pycon

    >>> node.swap(node['3'], node['4'])
    >>> node.keys()
    ['0', '1', '2', '4', '3']

Case last 2, a > b:

.. code-block:: pycon

    >>> node.swap(node['3'], node['4'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case neighbors, a < b:

.. code-block:: pycon

    >>> node.swap(node['1'], node['2'])
    >>> node.keys()
    ['0', '2', '1', '3', '4']

Case neighbors, a > b:

.. code-block:: pycon

    >>> node.swap(node['1'], node['2'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case non neighbors, one node first, a < b:

.. code-block:: pycon

    >>> node.swap(node['0'], node['2'])
    >>> node.keys()
    ['2', '1', '0', '3', '4']

Case non neighbors, one node first, a > b:

.. code-block:: pycon

    >>> node.swap(node['0'], node['2'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case non neighbors, one node last, a < b:

.. code-block:: pycon

    >>> node.swap(node['2'], node['4'])
    >>> node.keys()
    ['0', '1', '4', '3', '2']

Case non neighbors, one node last, a > b:

.. code-block:: pycon

    >>> node.swap(node['2'], node['4'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']

Case non neighbors, a < b:

.. code-block:: pycon

    >>> node.swap(node['1'], node['3'])
    >>> node.keys()
    ['0', '3', '2', '1', '4']

Case non neighbors, a > b:

.. code-block:: pycon

    >>> node.swap(node['1'], node['3'])
    >>> node.keys()
    ['0', '1', '2', '3', '4']


Order with References
---------------------

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     Order,
    ...     Reference,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class OrderReferenceNode(object):
    ...     pass

    >>> node = OrderReferenceNode(name='root')
    >>> node['child1'] = OrderReferenceNode()
    >>> node['child3'] = OrderReferenceNode()
    >>> node['child4'] = OrderReferenceNode()
    >>> node['child2'] = OrderReferenceNode()
    >>> node['child5'] = OrderReferenceNode()

    >>> node.insertbefore(node['child2'], node['child1'])
    Traceback (most recent call last):
      ...
    KeyError: u'Given node already contained in tree.'

    >>> len(node._index.keys())
    6

    >>> detached = node.detach('child4')
    >>> detached
    <OrderReferenceNode object 'child4' at ...>

    >>> len(detached._index.keys())
    1
    >>> len(node._index.keys())
    5
    >>> len(node.values())
    4

    >>> node.insertbefore(detached, node['child1'])
    >>> node.printtree()
    <class 'OrderReferenceNode'>: root
      <class 'OrderReferenceNode'>: child4
      <class 'OrderReferenceNode'>: child1
      <class 'OrderReferenceNode'>: child3
      <class 'OrderReferenceNode'>: child2
      <class 'OrderReferenceNode'>: child5

Merge 2 Node Trees:

.. code-block:: pycon

    >>> tree1 = OrderReferenceNode()
    >>> tree1['a'] = OrderReferenceNode()
    >>> tree1['b'] = OrderReferenceNode()
    >>> tree2 = OrderReferenceNode()
    >>> tree2['d'] = OrderReferenceNode()
    >>> tree2['e'] = OrderReferenceNode()
    >>> tree1._index is tree2._index
    False

    >>> len(tree1._index.keys())
    3

    >>> tree1.printtree()
    <class 'OrderReferenceNode'>: None
      <class 'OrderReferenceNode'>: a
      <class 'OrderReferenceNode'>: b

    >>> len(tree2._index.keys())
    3

    >>> tree2.printtree()
    <class 'OrderReferenceNode'>: None
      <class 'OrderReferenceNode'>: d
      <class 'OrderReferenceNode'>: e

    >>> tree1['c'] = tree2
    >>> len(tree1._index.keys())
    6

    >> sorted(tree1._index.values(), key=lambda x: x.__name__)

    >>> tree1._index is tree2._index
    True

    >>> tree1.printtree()
    <class 'OrderReferenceNode'>: None
      <class 'OrderReferenceNode'>: a
      <class 'OrderReferenceNode'>: b
      <class 'OrderReferenceNode'>: c
        <class 'OrderReferenceNode'>: d
        <class 'OrderReferenceNode'>: e

Detach subtree and insert elsewhere:

.. code-block:: pycon

    >>> sub = tree1.detach('c')
    >>> sub.printtree()
    <class 'OrderReferenceNode'>: c
      <class 'OrderReferenceNode'>: d
      <class 'OrderReferenceNode'>: e

    >>> tree1._index is sub._index
    False

    >>> sub._index is sub['d']._index is sub['e']._index
    True

    >>> len(sub._index.keys())
    3

    >>> tree1.printtree()
    <class 'OrderReferenceNode'>: None
      <class 'OrderReferenceNode'>: a
      <class 'OrderReferenceNode'>: b

    >>> len(tree1._index.keys())
    3

    >>> sub.__name__ = 'x'
    >>> tree1.insertbefore(sub, tree1['a'])
    >>> tree1.printtree()
    <class 'OrderReferenceNode'>: None
      <class 'OrderReferenceNode'>: x
        <class 'OrderReferenceNode'>: d
        <class 'OrderReferenceNode'>: e
      <class 'OrderReferenceNode'>: a
      <class 'OrderReferenceNode'>: b

    >>> tree1._index is sub._index
    True

    >>> len(tree1._index.keys())
    6

    >>> tree1.insertbefore(sub, tree1['a'])
    Traceback (most recent call last):
      ...
    KeyError: u'Given node already contained in tree.'

    >>> tree2.printtree()
    <class 'OrderReferenceNode'>: x
      <class 'OrderReferenceNode'>: d
      <class 'OrderReferenceNode'>: e

    >>> tree2['d'].allow_non_node_childs = True
    >>> tree2['d']['a'] = object()
    >>> tree2.printtree()
    <class 'OrderReferenceNode'>: x
      <class 'OrderReferenceNode'>: d
        a: <object object at ...>
      <class 'OrderReferenceNode'>: e

    >>> tree2.detach('d')
    <OrderReferenceNode object 'd' at ...>

    >>> tree2.printtree()
    <class 'OrderReferenceNode'>: x
      <class 'OrderReferenceNode'>: e

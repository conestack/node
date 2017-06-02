Fallback
========

Prepare test
------------

Required Imports:

.. code-block:: pycon

    >>> from node.behaviors import Adopt
    >>> from node.behaviors import Attributes
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Fallback
    >>> from node.behaviors import NodeChildValidate
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from plumber import plumbing

Attributes Node for testing:

.. code-block:: pycon

    >>> @plumbing(
    ...     Nodespaces,
    ...     Fallback,
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackNodeAttributes(object):
    ...     pass

Normal Node for testing:

.. code-block:: pycon

    >>> @plumbing(
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Adopt,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackNode(object):
    ...     attributes_factory = FallbackNodeAttributes


Setup test data
---------------

Define a root node:

.. code-block:: pycon

    >>> fb_node = FallbackNode(name='root')

It has a fallback subtree defined:

.. code-block:: pycon

    >>> fb_node.fallback_key = 'x'

The fallback subtree defines a fallback sub tree for itself.
Note that attrs internally is also a tree!:

.. code-block:: pycon

    >>> fb_node['x'] = FallbackNode()
    >>> fb_node['x'].fallback_key = '1'

Define node without fallback, but with data:

.. code-block:: pycon

    >>> fb_node['x']['1'] = FallbackNode()

An expected fallback value:

.. code-block:: pycon

    >>> fb_node['x']['1'].attrs['a'] = 1

An unexpected fallback value. To make them better visible, they are negative in
this test:

.. code-block:: pycon

    >>> fb_node['x']['1'].attrs['d'] = -3

Same on a second node for a different use case, where it find the value on this
level:

.. code-block:: pycon

    >>> fb_node['x']['2'] = FallbackNode()
    >>> fb_node['x']['2'].attrs['b'] = 2
    >>> fb_node['x']['2'].attrs['d'] = -2

Define a second subtree:

.. code-block:: pycon

    >>> fb_node['y'] = FallbackNode()

Here we have also a subtree which acts as fallback:

.. code-block:: pycon

    >>> fb_node['y'].fallback_key = '1'

Again some data-only nodes in the subtree, still a fallback use case:

.. code-block:: pycon

    >>> fb_node['y']['1'] = FallbackNode()
    >>> fb_node['y']['1'].attrs['c'] = 3
    >>> fb_node['y']['1'].attrs['d'] = -1

Define the node where our tests will look for the value:

.. code-block:: pycon

    >>> fb_node['y']['2'] = FallbackNode()
    >>> fb_node['y']['2'].attrs['d'] = 4

Visualize the tree:

.. code-block:: pycon

    >>> fb_node.printtree()
    <class 'FallbackNode'>: root
      <class 'FallbackNode'>: x
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2
      <class 'FallbackNode'>: y
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2


Test fallback behavior
----------------------

We always ask for attributes in the path 'root, y, 2, attrs'.
'attrs' is in fact a nodespace '__attributes__', but internally its handled
like contained. See nodespaces for more info on it, this is not fallback
specific.


Case 1
~~~~~~

Directly ask for the key 'd':

.. code-block:: pycon

    >>> fb_node['y']['2'].attrs['d']
    4


Case 2
~~~~~~

Ask for a key 'c' which does not exist in path. Now after not finding it there
it goes up one level to 'root, y'. Here it looks if there is a fallback defined.
There is one, its the subtree 'root, y, 1'. Now it looks there relative in
'attrs' for 'c' and has a hit. Value returned.:

.. code-block:: pycon

    >>> fb_node['y']['2'].attrs['c']
    3


Case 3
~~~~~~

Ask for a key 'b' which does not exist in the path. Now after not finding it
there it goes up one level to 'root, y'. Here it looks if there is a fallback
defined. There is one, its the subtree 'root, y, 1'. It looks there relative in
attrs for 'b' and it does not exist. After not finding it there it goes up one
level to 'root, y'. It has a fallback, but that one was already visited. Now it
goes up another level on 'root' and looks if there is a fallback defined. There
is one, its the subtree 'root, x'. Now it looks there relative for path
'2, attrs, b' and has a hit. Value returned.:

.. code-block:: pycon

    >>> fb_node['y']['2'].attrs['b']
    2


Case 4
~~~~~~

Ask for a key 'a' which does not exist in the path. Now after not finding it
there it goes up one level to 'root, y'. Here it looks if there is a fallback
defined. There is one, its the subtree 'root, y, 1'. It looks there relative in
attrs for a and it does not exist. After not finding it there it goes up one
level to 'root, y'. It has a fallback, but that one was already visited.
Now it goes up another level on 'root' and looks if there is a fallback defined.
There is one, its the subtree 'root, x'. Now it looks there relative for path
'2, attrs, a' and it does not exist. After not finding it there it goes up one
level to 'root, x'. Here it looks if there is a fallback defined. There is one,
its the subtree 'root, x, 1'. Now it looks there relative for path 'attrs, a'
and hit! Return value.:

.. code-block:: pycon

    >>> fb_node['y']['2'].attrs['a']
    1


Case 5
~~~~~~

When there is no fallback defined. We ask for a key 'z' which does not exist in
the path. Now after not finding it there it goes up one level to 'root, y'.
Here it looks if there is a fallback defined. There is one, its the subtree
'root, y, 1'. It looks there relative in attrs for z and it does not exist.
After not finding it there it goes up one level to 'root, y'. It has a
fallback, but that one was already visited. Now it goes up another level on
'root' and looks if there is a fallback defined. There is one, its the subtree
'root, x'. Now it looks there relative for path '2, attrs, z' and it does not
exist. After not finding it there it goes up one level to 'root, x'. Here it
looks if there is a fallback defined. There is one, its the subtree
'root, x, 1'. Now it looks there relative for path 'attrs, z' and it does not
exist. After not finding it there it goes up one level to 'root'. It has a
fallback, but that one was already visited. Next parent is None. Exit. No value
found. Raise KeyError:

.. code-block:: pycon

    >>> fb_node['y']['2'].attrs['z']
    Traceback (most recent call last):
    ...
    KeyError: 'z'

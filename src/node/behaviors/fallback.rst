=======================
node.behaviors.fallback
=======================

Prepare test
============

Prepare code
------------

Required Imports::

    >>> from node.behaviors import Adopt
    >>> from node.behaviors import Attributes
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Fallback
    >>> from node.behaviors import NodeChildValidate
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from plumber import plumbing

Attribute Node for testing::

    >>> @plumbing(
    ...     Nodespaces,
    ...     Fallback,
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackAttributeNode(object):
    ...     pass

Normal Node for testing::

    >>> @plumbing(
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Adopt,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackNode(object):
    ...     attributes_factory = FallbackAttributeNode

Setup test data
---------------

We define a root node::

    >>> no = FallbackNode(name='root')

It has a fallback subtree defined::

    >>> no.fallback_key = 'x'


Also the fallback subtree defines for itself a fallback sub tree.
Note that attrs internally is also a tree!

::

    >>> no['x'] = FallbackNode()
    >>> no['x'].fallback_key = '1'

Now lest define tow node without fallback, but with data::

    >>> no['x']['1'] = FallbackNode()

An expected fallback value::

    >>> no['x']['1'].attrs['a'] = 1

An unexpected fallback value, to make them better visible,
they are negative in this test::

    >>> no['x']['1'].attrs['d'] = -3

Same on a second node for a different use case, where it find the value on this level::

    >>> no['x']['2'] = FallbackNode()
    >>> no['x']['2'].attrs['b'] = 2
    >>> no['x']['2'].attrs['d'] = -2

Now define a second subtree::

    >>> no['y'] = FallbackNode()

Here we have also a subtree which acts as fallback!

::

    >>> no['y'].fallback_key = '1'

Again some data only nodes in the subtree, still a fallback use case::

    >>> no['y']['1'] = FallbackNode()
    >>> no['y']['1'].attrs['c'] = 3
    >>> no['y']['1'].attrs['d'] = -1

Last the node where our tests will look for the value::

    >>> no['y']['2'] = FallbackNode()
    >>> no['y']['2'].attrs['d'] = 4

Visualize the tree::

    >>> no.printtree()
    <class 'FallbackNode'>: root
      <class 'FallbackNode'>: x
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2
      <class 'FallbackNode'>: y
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2

Testing
=======

We always ask for attributes in the path 'root, y, 2, attrs'!
'attrs' is in fact a nodespace '__attributes__', but internally its handled like contained!
See nodespaces for more info on it, this is not fallback specific.

Case 1:
We directly ask for the key 'd'.

::

    >>> no['y']['2'].attrs['d']
    4

Case 2:
We ask for a key 'c' which does not exist in the path.
Now after not finding it there it goes up one level to 'root, y'.
here it looks if there is a fallback defined.
There is one, its the subtree 'root, y, 1'.
Now it looks there relative in 'attrs' for 'c' and has a hit. Value returned.

::

    >>> no['y']['2'].attrs['c']
    3

Case 2:
We ask for a key 'b' which does not exist in the path.
Now after not finding it there it goes up one level to 'root, y'.
Here it looks if there is a fallback defined.
There is one, its the subtree 'root, y, 1'.
It looks there relative in attrs for b and it does not exist.
After not finding it there it goes up one level to 'root, y'.
It has a fallback, but that one was already visited.
Now it goes up another level on 'root' and looks if there is a fallback defined.
There is one, its the subtree 'root, x'.
Now it looks there relative for path '2, attrs, b' and has a hit. Value returned.

::

    >>> no['y']['2'].attrs['b']
    2

Case 2:
We ask for a key 'a' which does not exist in the path.
Now after not finding it there it goes up one level to 'root, y'.
Here it looks if there is a fallback defined.
There is one, its the subtree 'root, y, 1'.
It looks there relative in attrs for a and it does not exist.
After not finding it there it goes up one level to 'root, y'.
It has a fallback, but that one was already visited.
Now it goes up another level on 'root' and looks if there is a fallback defined.
There is one, its the subtree 'root, x'.
Now it looks there relative for path '2, attrs, a' and it does not exist.
After not finding it there it goes up one level to 'root, x'.
Here it looks if there is a fallback defined.
There is one, its the subtree 'root, x, 1'.
Now it looks there relative for path 'attrs, a' and hit! Return value.

::

    >>> no['y']['2'].attrs['a']
    1

Case 2:
When there is no fallback defined.
We ask for a key 'z' which does not exist in the path.
Now after not finding it there it goes up one level to 'root, y'.
Here it looks if there is a fallback defined.
There is one, its the subtree 'root, y, 1'.
It looks there relative in attrs for z and it does not exist.
After not finding it there it goes up one level to 'root, y'.
It has a fallback, but that one was already visited.
Now it goes up another level on 'root' and looks if there is a fallback defined.
There is one, its the subtree 'root, x'.
Now it looks there relative for path '2, attrs, z' and it does not exist.
After not finding it there it goes up one level to 'root, x'.
Here it looks if there is a fallback defined.
There is one, its the subtree 'root, x, 1'.
Now it looks there relative for path 'attrs, z' and it does not exist.
After not finding it there it goes up one level to 'root'.
It has a fallback, but that one was already visited.
Next parent is None. Exit. No value found. raise KeyError.

::

    >>> no['y']['2'].attrs['z']
    Traceback (most recent call last):
    ...
    KeyError: 'z'


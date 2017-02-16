Invalidate
==========

Required Imports:

.. code-block:: pycon

    >>> from plumber import plumbing
    >>> from node.interfaces import ICache
    >>> from node.interfaces import IInvalidate
    >>> from node.behaviors import Adopt
    >>> from node.behaviors import Cache
    >>> from node.behaviors import Invalidate
    >>> from node.behaviors import VolatileStorageInvalidate
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from node.behaviors import ChildFactory


Default Invalidation
--------------------

When using default ``Invalidate``, Contents of node just gets deleted.
Be aware this implementation must not be used on persisting nodes.

Build invalidating node:

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     Invalidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class Node(object):
    ...     pass

Test tree:

.. code-block:: pycon

    >>> root = Node()
    >>> root['c1'] = Node()
    >>> root['c2'] = Node()
    >>> root['c2']['d1'] = Node()
    >>> root['c2']['d2'] = Node()

    >>> IInvalidate.providedBy(root)
    True
    >>> ICache.providedBy(root)
    False

    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c1
      <class 'Node'>: c2
        <class 'Node'>: d1
        <class 'Node'>: d2

Active invalidation of child by key:

.. code-block:: pycon

    >>> root.invalidate(key='c1')
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c2
        <class 'Node'>: d1
        <class 'Node'>: d2

    >>> root.invalidate(key='c1')
    Traceback (most recent call last):
      ...
    KeyError: 'c1'

Active invalidation of all children:

.. code-block:: pycon

    >>> root['c2'].invalidate()
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c2


Volatile Storage Invalidate
---------------------------

When a node internally uses a volatile storage like ``DictStorage`` or
``OdictStorage``, some can use ``VolatileStorageInvalidate`` for invalidation:

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     VolatileStorageInvalidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class Node(object):
    ...     pass

Test tree:

.. code-block:: pycon

    >>> root = Node()
    >>> root['c1'] = Node()
    >>> root['c2'] = Node()
    >>> root['c2']['d1'] = Node()
    >>> root['c2']['d2'] = Node()

    >>> IInvalidate.providedBy(root)
    True
    >>> ICache.providedBy(root)
    False

    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c1
      <class 'Node'>: c2
        <class 'Node'>: d1
        <class 'Node'>: d2

Active invalidation of child by key:

.. code-block:: pycon

    >>> root.invalidate(key='c1')
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c2
        <class 'Node'>: d1
        <class 'Node'>: d2

    >>> root.invalidate(key='c1')
    Traceback (most recent call last):
      ...
    KeyError: 'c1'

Active invalidation of all children:

.. code-block:: pycon

    >>> root['c2'].invalidate()
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c2

Check for ChildFactory Node:

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     VolatileStorageInvalidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     ChildFactory,
    ...     OdictStorage)
    ... class Node(object):
    ...     factories = {
    ...         'foo': Node,
    ...         'bar': Node,
    ...     }
    >>> node = Node()
    >>> node.items()
    [('foo', <Node object 'foo' at ...>), 
    ('bar', <Node object 'bar' at ...>)]

    >>> node.invalidate('foo')
    >>> node.keys()
    ['foo', 'bar']

    >>> node.storage.items()
    [('bar', <Node object 'bar' at ...>)]

    >>> node.invalidate('foo')
    >>> node.storage.items()
    [('bar', <Node object 'bar' at ...>)]

    >>> node.invalidate()
    >>> node.storage.items()
    []

    >>> node.invalidate('baz')
    Traceback (most recent call last):
      ...
    KeyError: 'baz'


Caching
-------

Build a node with active invalidation and cache functionality:

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     Cache,
    ...     Invalidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class Node(object):
    ...     pass

    >>> root = Node()
    >>> root['c1'] = Node()
    >>> root['c2'] = Node()
    >>> root['c2']['d1'] = Node()
    >>> root['c2']['d2'] = Node()

    >>> IInvalidate.providedBy(root)
    True
    >>> ICache.providedBy(root)
    True

We just accessed 'c2' above, only cached value on root at the moment:

.. code-block:: pycon

    >>> root.cache
    {'c2': <Node object 'c2' at ...>}

    >>> root['c1']
    <Node object 'c1' at ...>

After accessing 'c1', it is cached as well:

.. code-block:: pycon

    >>> root.cache
    {'c2': <Node object 'c2' at ...>, 
    'c1': <Node object 'c1' at ...>}

Invalidate plumbing removes item from cache:

.. code-block:: pycon

    >>> root.invalidate(key='c1')
    >>> root.cache
    {'c2': <Node object 'c2' at ...>}

    >>> root.invalidate()
    >>> root.cache
    {}

    >>> root.printtree()
    <class 'Node'>: None

Test invalidation plumbing hook with missing cache values:

.. code-block:: pycon

    >>> root['x1'] = Node()
    >>> root['x2'] = Node()
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: x1
      <class 'Node'>: x2

    >>> root.cache
    {'x2': <Node object 'x2' at ...>, 
    'x1': <Node object 'x1' at ...>}

    >>> del root.cache['x1']
    >>> del root.cache['x2']

    >>> root.invalidate(key='x1')
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: x2

    >>> del root.cache['x2']
    >>> root.invalidate()
    >>> root.printtree()
    <class 'Node'>: None

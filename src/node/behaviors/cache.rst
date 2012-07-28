node.behaviors.invalidate
=========================

::

    >>> from plumber import plumber
    >>> from node.interfaces import (
    ...     ICache,
    ...     IInvalidate,
    ... )
    >>> from node.behaviors import (
    ...     Adopt,
    ...     Cache,
    ...     Invalidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage,
    ... )

Build a node with active invalidation functionality::

    >>> class Node(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Adopt, 
    ...         Invalidate, 
    ...         DefaultInit,
    ...         Nodify, 
    ...         OdictStorage,
    ...     )

Test tree::

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

Active invalidation of child by key::
    
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

Active invalidation of all children::

    >>> root['c2'].invalidate()
    >>> root.printtree()
    <class 'Node'>: None
      <class 'Node'>: c2


node.behaviors.cache
====================

Build a node with active invalidation and cache functionality::

    >>> class Node(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Adopt, 
    ...         Cache, 
    ...         Invalidate, 
    ...         DefaultInit,
    ...         Nodify, 
    ...         OdictStorage,
    ...     )
    
    >>> root = Node()
    >>> root['c1'] = Node()
    >>> root['c2'] = Node()
    >>> root['c2']['d1'] = Node()
    >>> root['c2']['d2'] = Node()
    
    >>> IInvalidate.providedBy(root)
    True
    >>> ICache.providedBy(root)
    True

We just accessed 'c2' above, only cached value on root at the moment::

    >>> root.cache
    {'c2': <Node object 'c2' at ...>}
    
    >>> root['c1']
    <Node object 'c1' at ...>

After accessing 'c1', it is cached as well::

    >>> root.cache
    {'c2': <Node object 'c2' at ...>, 
    'c1': <Node object 'c1' at ...>}

Invalidate plumbing removes item from cache::

    >>> root.invalidate(key='c1')
    >>> root.cache
    {'c2': <Node object 'c2' at ...>}

    >>> root.invalidate()
    >>> root.cache
    {}
    
    >>> root.printtree()
    <class 'Node'>: None

Test invalidation plumbing hook with missing cache values::

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

node.parts.Nodify
-----------------

    >>> from plumber import plumber

    >>> from node.testing import FullMappingTester
    >>> from node.parts import (
    ...     Adopt,
    ...     DictStorage,
    ...     DefaultInit,
    ...     Nodify,
    ... )

    >>> class Node(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Adopt, DefaultInit, Nodify, DictStorage
    
    >>> root = Node(name='root')
    >>> root['child'] = Node()
    >>> root.name
    'root'
    
    >>> root.parent
    
    >>> child = root['child']
    >>> child.name
    'child'
    
    >>> child.parent
    <Node object 'root' at ...>
    
    >>> root.printtree()
    <class 'Node'>: root
      <class 'Node'>: child
      
    >>> bool(root)
    True

    >>> tester = FullMappingTester(Node)
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

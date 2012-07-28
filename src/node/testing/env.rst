node.testing.env
================

::

    >>> from node.testing.env import MyNode
    >>> mynode = MyNode()

IFullMapping
------------

``__setitem__``::

    >>> mynode['foo'] = MyNode()
    >>> mynode['bar'] = MyNode(name='xxx')

``__getitem__``::

    >>> mynode['foo']
    <MyNode object 'foo' at ...>
    
    >>> mynode['bar'].__name__
    'bar'

``get``::

    >>> mynode.get('bar')
    <MyNode object 'bar' at ...>
    
    >>> mynode.get('xxx', 'default')
    'default'

``__iter__``::

    >>> [key for key in mynode]
    ['foo', 'bar']
    

``keys``::

    >>> mynode.keys()
    ['foo', 'bar']

``iterkeys``::

    >>> [key for key in mynode.iterkeys()]
    ['foo', 'bar']

``values``::

    >>> mynode.values()
    [<MyNode object 'foo' at ...>, <MyNode object 'bar' at ...>]

``itervalues``::

    >>> [val for val in mynode.itervalues()]
    [<MyNode object 'foo' at ...>, <MyNode object 'bar' at ...>]

``items``::

    >>> mynode.items()
    [('foo', <MyNode object 'foo' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]

``iteritems``::

    >>> [item for item in mynode.iteritems()]
    [('foo', <MyNode object 'foo' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]

``__contains__``::

    >>> 'bar' in mynode
    True

``has_key``::

    >>> mynode.has_key('foo')
    True

``__len__``::

    >>> len(mynode)
    2

``update``::

    >>> mynode.update((('baz', MyNode()),))
    >>> mynode['baz']
    <MyNode object 'baz' at ...>

``__delitem__``::

    >>> del mynode['bar']
    >>> mynode.keys()
    ['foo', 'baz']

``copy``::

    >>> mycopied = mynode.copy()
    >>> mycopied
    <MyNode object 'None' at ...>
    
    >>> mycopied is mynode
    False
    
    >>> mycopied.items()
    [('foo', <MyNode object 'foo' at ...>), 
    ('baz', <MyNode object 'baz' at ...>)]
    
    >>> mycopied['foo'] is mynode['foo']
    True

``setdefault``::

    >>> mynew = MyNode()
    >>> mynode.setdefault('foo', mynew) is mynew
    False
    
    >>> mynode.setdefault('bar', mynew) is mynew
    True
    
    >>> mynode.items()
    [('foo', <MyNode object 'foo' at ...>), 
    ('baz', <MyNode object 'baz' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]

``pop``::

    >>> mynode.pop('xxx')
    Traceback (most recent call last):
      ...
    KeyError: 'xxx'
    
    >>> mynode.pop('xxx', 'default')
    'default'
    
    >>> mynode.pop('foo')
    <MyNode object 'foo' at ...>
    
    >>> mynode.keys()
    ['baz', 'bar']

``popitem`` and ``clear``::

    >>> mynode.popitem()
    ('bar', <MyNode object 'bar' at ...>)
    
    >>> mynode.keys()
    ['baz']
    
    >>> mynode.clear()
    >>> mynode.keys()
    []
    
    >>> mynode.popitem()
    Traceback (most recent call last):
      ...
    KeyError: 'popitem(): mapping is empty'

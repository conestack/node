node.testing.env
================

.. code-block:: pycon

    >>> from node.testing.env import MyNode
    >>> mynode = MyNode()

IFullMapping
------------

__setitem__
~~~~~~~~~~~

.. code-block:: pycon

    >>> mynode['foo'] = MyNode()
    >>> mynode['bar'] = MyNode(name='xxx')


__getitem__
~~~~~~~~~~~

.. code-block:: pycon

    >>> mynode['foo']
    <MyNode object 'foo' at ...>

    >>> mynode['bar'].__name__
    'bar'


get
~~~

.. code-block:: pycon

    >>> mynode.get('bar')
    <MyNode object 'bar' at ...>

    >>> mynode.get('xxx', 'default')
    'default'


__iter__
~~~~~~~~

.. code-block:: pycon

    >>> [key for key in mynode]
    ['foo', 'bar']


keys
~~~~

.. code-block:: pycon

    >>> mynode.keys()
    ['foo', 'bar']


iterkeys
~~~~~~~~

.. code-block:: pycon

    >>> [key for key in mynode.iterkeys()]
    ['foo', 'bar']


values
~~~~~~

.. code-block:: pycon

    >>> mynode.values()
    [<MyNode object 'foo' at ...>, <MyNode object 'bar' at ...>]


itervalues
~~~~~~~~~~

.. code-block:: pycon

    >>> [val for val in mynode.itervalues()]
    [<MyNode object 'foo' at ...>, <MyNode object 'bar' at ...>]


items
~~~~~

.. code-block:: pycon

    >>> mynode.items()
    [('foo', <MyNode object 'foo' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]


iteritems
~~~~~~~~~

.. code-block:: pycon

    >>> [item for item in mynode.iteritems()]
    [('foo', <MyNode object 'foo' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]


__contains__
~~~~~~~~~~~~

.. code-block:: pycon

    >>> 'bar' in mynode
    True


has_key
~~~~~~~

.. code-block:: pycon

    >>> mynode.has_key('foo')
    True


__len__
~~~~~~~

.. code-block:: pycon

    >>> len(mynode)
    2


update
~~~~~~

.. code-block:: pycon

    >>> mynode.update((('baz', MyNode()),))
    >>> mynode['baz']
    <MyNode object 'baz' at ...>


__delitem__
~~~~~~~~~~~

.. code-block:: pycon

    >>> del mynode['bar']
    >>> mynode.keys()
    ['foo', 'baz']


copy
~~~~

.. code-block:: pycon

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


setdefault
~~~~~~~~~~

.. code-block:: pycon

    >>> mynew = MyNode()
    >>> mynode.setdefault('foo', mynew) is mynew
    False

    >>> mynode.setdefault('bar', mynew) is mynew
    True

    >>> mynode.items()
    [('foo', <MyNode object 'foo' at ...>), 
    ('baz', <MyNode object 'baz' at ...>), 
    ('bar', <MyNode object 'bar' at ...>)]


pop
~~~

.. code-block:: pycon

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


popitem and clear
~~~~~~~~~~~~~~~~~

.. code-block:: pycon

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

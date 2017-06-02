Abstract Storage
----------------

.. code-block:: pycon

    >>> from plumber import plumbing
    >>> from node.behaviors import Storage

    >>> @plumbing(Storage)
    ... class StorageObject(object):
    ...     pass

    >>> obj = StorageObject()
    >>> obj.storage
    Traceback (most recent call last):
      ...
    NotImplementedError: Abstract storage does not implement ``storage``


Dict Storage
------------

.. code-block:: pycon

    >>> from node.behaviors import DictStorage

    >>> @plumbing(DictStorage)
    ... class StorageObject(object):
    ...     pass

    >>> obj = StorageObject()
    >>> obj.storage
    {}

    >>> obj['foo'] = 'foo'
    >>> obj.storage
    {'foo': 'foo'}

    >>> obj['foo']
    'foo'

    >>> [key for key in obj]
    ['foo']

    >>> del obj['foo']
    >>> obj.storage
    {}


Odict Storage
-------------

.. code-block:: pycon

    >>> from node.behaviors import OdictStorage

    >>> @plumbing(OdictStorage)
    ... class StorageObject(object):
    ...     pass

    >>> obj = StorageObject()
    >>> obj.storage
    odict()

    >>> obj['foo'] = 'foo'
    >>> obj.storage
    odict([('foo', 'foo')])

    >>> obj['foo']
    'foo'

    >>> [key for key in obj]
    ['foo']

    >>> del obj['foo']
    >>> obj.storage
    odict()

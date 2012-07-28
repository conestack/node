Abstract storage::

    >>> from plumber import plumber
    >>> from node.behaviors import Storage
    >>> class StorageObject(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Storage
    
    >>> obj = StorageObject()
    >>> obj.storage
    Traceback (most recent call last):
      ...
    NotImplementedError: Abstract storage does not implement ``storage``

Dict Storage::

    >>> from node.behaviors import DictStorage
    >>> class StorageObject(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = DictStorage
    
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

Odict Storage::

    >>> from node.behaviors import OdictStorage
    >>> class StorageObject(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = OdictStorage
    
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

node.behaviors.FullMapping
--------------------------

Plumber and FullMappingTester.::

    >>> from plumber import plumber
    >>> from node.testing import FullMappingTester

A full mapping that is going to fail, because nobody takes care of
``__delitem__``, ``__getitem__``, ``__iter__`` and ``__setitem__``.::

    >>> from node.behaviors import FullMapping
    >>> class MyFullMapping(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = FullMapping

    >>> tester = FullMappingTester(MyFullMapping, include_node_checks=False)
    >>> tester.run()
    >>> tester.combined
    ``__contains__``: failed: NotImplementedError()
    ``__delitem__``: failed: NotImplementedError()
    ``__getitem__``: failed: NotImplementedError()
    ``__iter__``: failed: NotImplementedError()
    ``__len__``: failed: NotImplementedError()
    ``__setitem__``: failed: NotImplementedError()
    ``clear``: failed: NotImplementedError()
    ``copy``: failed: NotImplementedError()
    ``get``: failed: NotImplementedError()
    ``has_key``: failed: NotImplementedError()
    ``items``: failed: NotImplementedError()
    ``iteritems``: failed: NotImplementedError()
    ``iterkeys``: failed: NotImplementedError()
    ``itervalues``: failed: NotImplementedError()
    ``keys``: failed: NotImplementedError()
    ``pop``: failed: NotImplementedError()
    ``popitem``: failed: NotImplementedError()
    ``setdefault``: failed: NotImplementedError()
    ``update``: failed: NotImplementedError()
    ``values``: failed: NotImplementedError()

All methods are defined on the class by the FullMapping behavior, none are
inherited from base classes.::

    >>> tester.wherefrom
    __contains__:  MyFullMapping
    __delitem__:  MyFullMapping
    __getitem__:  MyFullMapping
    __iter__:  MyFullMapping
    __len__:  MyFullMapping
    __setitem__:  MyFullMapping
    clear:  MyFullMapping
    copy:  MyFullMapping
    get:  MyFullMapping
    has_key:  MyFullMapping
    items:  MyFullMapping
    iteritems:  MyFullMapping
    iterkeys:  MyFullMapping
    itervalues:  MyFullMapping
    keys:  MyFullMapping
    pop:  MyFullMapping
    popitem:  MyFullMapping
    setdefault:  MyFullMapping
    update:  MyFullMapping
    values:  MyFullMapping

Use a storage.::

    >>> from node.behaviors import DictStorage
    >>> class MyFullMapping(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = FullMapping, DictStorage

    >>> tester = FullMappingTester(MyFullMapping, include_node_checks=False)
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

Only the Four were taken from the base class, the others were filled in by the
FullMapping behavior.::

    >>> tester.wherefrom
    __contains__:  MyFullMapping
    __delitem__:  MyFullMapping
    __getitem__:  MyFullMapping
    __iter__:  MyFullMapping
    __len__:  MyFullMapping
    __setitem__:  MyFullMapping
    clear:  MyFullMapping
    copy:  MyFullMapping
    get:  MyFullMapping
    has_key:  MyFullMapping
    items:  MyFullMapping
    iteritems:  MyFullMapping
    iterkeys:  MyFullMapping
    itervalues:  MyFullMapping
    keys:  MyFullMapping
    pop:  MyFullMapping
    popitem:  MyFullMapping
    setdefault:  MyFullMapping
    update:  MyFullMapping
    values:  MyFullMapping

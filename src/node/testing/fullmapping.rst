node.testing.fullmapping
========================

FullMappingTester
-----------------

::

    >>> from node.testing import FullMappingTester
    
    >>> class TestMapping(object):
    ...     def __init__(self):
    ...         self.data = dict()
    
    >>> class TestNode(TestMapping):
    ...     def __init__(self, name=None, parent=None):
    ...         super(TestNode, self).__init__()
    ...         self.__name__ = name
    ...         self.__parent__ = parent

``__setitem__``::

    >>> fmtester = FullMappingTester(TestMapping)
    >>> fmtester.test___setitem__()
    Traceback (most recent call last):
      ...
    TypeError: 'TestMapping' object does not support item assignment
    
    >>> class TestMappingSetItem(TestMapping):
    ...     def __setitem__(self, key, value):
    ...         self.data[key] = value
    
    >>> fmtester = FullMappingTester(TestMappingSetItem)
    >>> fmtester.test___setitem__()
    Traceback (most recent call last):
      ...
    TypeError: __init__() got an unexpected keyword argument 'name'
    
    >>> class TestNodeSetItem(TestNode, TestMappingSetItem): pass
    >>> fmtester = FullMappingTester(TestNodeSetItem)
    >>> fmtester.test___setitem__()
    
``__getitem__``::

    >>> fmtester = FullMappingTester(TestMapping)
    >>> fmtester.test___getitem__()
    Traceback (most recent call last):
      ...
    TypeError: 'TestMapping' ...
    
    >>> class TestMappingGetItem(TestMappingSetItem):
    ...     def __getitem__(self, key):
    ...         return self.data[key]
    
    >>> fmtester = FullMappingTester(TestMappingGetItem)
    >>> fmtester.context['foo'] = TestMappingGetItem()
    >>> fmtester.context['bar'] = TestMappingGetItem()
    >>> fmtester.test___getitem__()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingGetItem' object has no attribute '__name__'
    
    >>> class TestNodeGetItem(TestNodeSetItem, TestMappingGetItem): pass 
    >>> fmtester = FullMappingTester(TestNodeGetItem)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___getitem__()
    Traceback (most recent call last):
      ...
    Exception: Child ``bar`` has wrong ``__name__``
    
    >>> class TestNodeSetItem(TestNodeSetItem):
    ...     def __setitem__(self, name, value):
    ...         value.__parent__ = self
    ...         value.__name__ = name
    ...         self.data[name] = value
    
    >>> class TestNodeGetItem(TestNodeSetItem, TestMappingGetItem): pass 
    >>> fmtester = FullMappingTester(TestNodeGetItem)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___getitem__()

``get``::

    >>> fmtester.test_get()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestNodeGetItem' object has no attribute 'get'

    >>> class TestMappingGet(TestMappingGetItem):
    ...     def get(self, key, default=None):
    ...         return object()
    
    >>> fmtester = FullMappingTester(TestMappingGet, include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_get()
    Traceback (most recent call last):
      ...
    Exception: Expected default, got <object object at ...>
    
    >>> class TestMappingGet(TestMappingGetItem):
    ...     def get(self, key, default=None):
    ...         return default
    
    >>> fmtester = FullMappingTester(TestMappingGet, include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_get()
    Traceback (most recent call last):
      ...
    Exception: Expected value, got default
    
    >>> class TestMappingGet(TestMappingGetItem):
    ...     def get(self, key, default=None):
    ...         return self.data.get(key, default)
    
    >>> fmtester = FullMappingTester(TestMappingGet, include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_get()
    
``__iter__``::

    >>> fmtester = FullMappingTester(TestMapping)
    >>> fmtester.test___iter__()
    Traceback (most recent call last):
      ...
    TypeError: 'TestMapping' object is not iterable
    
    >>> class TestMappingIter(TestMappingGet):
    ...     def __iter__(self):
    ...         return iter(list())
    
    >>> fmtester = FullMappingTester(TestMappingIter)
    >>> fmtester.test___iter__()
    Traceback (most recent call last):
      ...
    Exception: Expected 2-length result. Got ``0``
    
    >>> class TestMappingIter(TestMappingGet):
    ...     def __iter__(self):
    ...         return iter(['a', 'b'])
    
    >>> fmtester = FullMappingTester(TestMappingIter)
    >>> fmtester.test___iter__()
    Traceback (most recent call last):
      ...
    Exception: Expected ``['a', 'b']`` as keys. Got ``['foo', 'bar']``
    
    >>> class TestMappingIter(TestMappingGet):
    ...     def __iter__(self):
    ...         return self.data.__iter__()
    
    >>> fmtester = FullMappingTester(TestMappingIter, include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___iter__()

``keys``::

    >>> fmtester.test_keys()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingIter' object has no attribute 'keys'
    
    >>> class TestMappingKeys(TestMappingIter):
    ...     def keys(self):
    ...         return [k for k in self.data]
    
    >>> fmtester = FullMappingTester(TestMappingKeys, include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_keys()

``iterkeys``::

    >>> fmtester.test_iterkeys()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingKeys' object has no attribute 'iterkeys'
    
    >>> class TestMappingIterKeys(TestMappingKeys):
    ...     def iterkeys(self):
    ...         return self.data.__iter__()
    
    >>> fmtester = FullMappingTester(TestMappingIterKeys,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_iterkeys()

``values``::

    >>> fmtester.test_values()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingIterKeys' object has no attribute 'values'
    
    >>> class TestMappingValues(TestMappingIterKeys):
    ...     def values(self):
    ...         return self.data.values()
    
    >>> fmtester = FullMappingTester(TestMappingValues,
    ...                              include_node_checks=False)
    >>> fmtester.test_values()
    Traceback (most recent call last):
      ...
    Exception: Expected 2-length result. Got ``0``
    
    >>> fmtester.test___setitem__()
    >>> fmtester.test_values()

    >>> fmtester = FullMappingTester(TestMappingValues)
    >>> fmtester.context['foo'] = TestMappingValues()
    >>> fmtester.context['bar'] = TestMappingValues()
    >>> fmtester.test_values()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingValues' object has no attribute '__name__'

    >>> class TestNodeValues(TestNode, TestMappingValues):
    ...     pass

    >>> fmtester = FullMappingTester(TestNodeValues)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_values()
    Traceback (most recent call last):
      ...
    Exception: Expected __name__ of value invalid. Got ``None``
    
    >>> class TestNodeValues(TestNodeSetItem, TestMappingValues):
    ...     pass
    
    >>> fmtester = FullMappingTester(TestNodeValues)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_values()

``itervalues``::

    >>> fmtester.test_itervalues()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestNodeValues' object has no attribute 'itervalues'
    
    >>> class TestMappingIterValues(TestMappingValues):
    ...     def itervalues(self):
    ...         return iter(self.data.values())
    
    >>> fmtester = FullMappingTester(TestMappingIterValues,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_itervalues()

``items``::

    >>> fmtester.test_items()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingIterValues' object has no attribute 'items'
    
    >>> class TestMappingItems(TestMappingIterValues):
    ...     def items(self):
    ...         return list()
    
    >>> fmtester = FullMappingTester(TestMappingItems,
    ...                              include_node_checks=False)
    >>> fmtester.test_items()
    Traceback (most recent call last):
      ...
    Exception: Expected 2-length result. Got ``0``
    
    >>> class TestMappingItems(TestMappingIterValues):
    ...     def items(self):
    ...         return [('foo', object()), ('b', object())]
    
    >>> fmtester = FullMappingTester(TestMappingItems,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_items()
    Traceback (most recent call last):
      ...
    Exception: Expected keys ``['foo', 'bar']``. Got ``b``
    
    >>> class TestMappingItems(TestMappingIterValues):
    ...     def items(self):
    ...         return [('foo', object()), ('bar', object())]
    
    >>> fmtester = FullMappingTester(TestMappingItems,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_items()
    Traceback (most recent call last):
      ...
    Exception: Expected <object object at ...>, got <TestMappingItems object at ...>
    
    >>> class TestMappingItems(TestMappingIterValues):
    ...     def items(self):
    ...         return self.data.items()
    
    >>> fmtester = FullMappingTester(TestMappingItems,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_items()
    
    >>> class TestNodeItems(TestNode, TestMappingItems):
    ...     pass
    
    >>> fmtester = FullMappingTester(TestNodeItems)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_items()
    Traceback (most recent call last):
      ...
    Exception: Expected same value for ``key`` "foo" and ``__name__`` "None"
    
    >>> class TestNodeItems(TestNodeSetItem, TestMappingItems):
    ...     pass
    
    >>> fmtester = FullMappingTester(TestNodeItems)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_items()

``iteritems``::

    >>> fmtester.test_iteritems()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestNodeItems' object has no attribute 'iteritems'
    
    >>> class TestMappingIterItems(TestMappingItems):
    ...     def iteritems(self):
    ...         return iter(self.data.items())
    
    >>> fmtester = FullMappingTester(TestMappingIterItems,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_iteritems()

``__contains__``::

    >>> class TestMappingContains(TestMappingIterItems):
    ...     def __contains__(self, key):
    ...         return False
    
    >>> fmtester = FullMappingTester(TestMappingContains,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___contains__()
    Traceback (most recent call last):
      ...
    Exception: Expected ``foo`` and ``bar`` return ``True`` by ``__contains__``
    
    >>> class TestMappingContains(TestMappingIterItems):
    ...     def __contains__(self, key):
    ...         return True
    >>> fmtester = FullMappingTester(TestMappingContains,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___contains__()
    Traceback (most recent call last):
      ...
    Exception: Expected __contains__ to return False for non-existent key
    
    >>> class TestMappingContains(TestMappingIterItems):
    ...     def __contains__(self, key):
    ...         return key in self.data
    
    >>> fmtester = FullMappingTester(TestMappingContains,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___contains__()

``has_key``::

    >>> fmtester.test_has_key()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingContains' object has no attribute 'has_key'
    
    >>> class TestMappingHasKey(TestMappingContains):
    ...     def has_key(self, key):
    ...         return False
    
    >>> fmtester = FullMappingTester(TestMappingHasKey,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_has_key()
    Traceback (most recent call last):
      ...
    Exception: Expected ``foo`` and ``bar`` return ``True`` by ``has_key``
    
    >>> class TestMappingHasKey(TestMappingContains):
    ...     def has_key(self, key):
    ...         return self.data.has_key(key)
    
    >>> fmtester = FullMappingTester(TestMappingHasKey,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_has_key()

``__len__``::

    >>> fmtester.test___len__()
    Traceback (most recent call last):
      ...
    TypeError: object of type 'TestMappingHasKey' has no len()
    
    >>> class TestMappingLen(TestMappingHasKey):
    ...     def __len__(self):
    ...         return 0
    
    >>> fmtester = FullMappingTester(TestMappingLen,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___len__()
    Traceback (most recent call last):
      ...
    Exception: Expected 2-length result. Got ``0``
    
    >>> class TestMappingLen(TestMappingHasKey):
    ...     def __len__(self):
    ...         return len(self.data)
    
    >>> fmtester = FullMappingTester(TestMappingLen,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test___len__()

``update``::

    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingLen' object has no attribute 'update'
    
    >>> class TestMappingUpdate(TestMappingLen):
    ...     def update(self, data=(), **kw):
    ...         pass
    
    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    Exception: KeyError, Expected ``baz`` and ``blub`` after update
    
    >>> class TestMappingUpdate(TestMappingLen):
    ...     def update(self, data=(), **kw):
    ...         for key, value in data:
    ...             self[key] = object()
    ...         for key, value in kw.iteritems():
    ...             self[key] = object()
    
    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    Exception: Object at ``baz`` not expected one after update
    
    >>> class TestMappingUpdate(TestMappingLen):
    ...     def update(self, data=(), **kw):
    ...         for key, value in data:
    ...             self[key] = value
    ...         for key, value in kw.iteritems():
    ...             self[key] = object()

    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    Exception: Object at ``blub`` not expected one after update

    >>> class BrokenData(dict):
    ...     def __delitem__(self, key):
    ...         if key == 'blub':
    ...             raise Exception(u"Broken implementation")
    
    >>> class TestMappingUpdate(TestMappingLen):
    ...     def __init__(self):
    ...         self.data = BrokenData()
    ...     def update(self, data=(), **kw):
    ...         for key, value in data:
    ...             self[key] = value
    ...         for key, value in kw.iteritems():
    ...             self[key] = value
    
    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    RuntimeError: Cannot del test key.
    
    >>> class TestMappingUpdate(TestMappingLen):
    ...     def update(self, data=(), data1=(), **kw):
    ...         for key, value in data:
    ...             self[key] = value
    ...         for key, value in kw.iteritems():
    ...             self[key] = value
    
    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()
    Traceback (most recent call last):
      ...
    Exception: Expected TypeError for update with more than one positional argument.

    >>> class TestMappingUpdate(TestMappingLen):
    ...     def update(self, data=(), **kw):
    ...         for key, value in data:
    ...             self[key] = value
    ...         for key, value in kw.iteritems():
    ...             self[key] = value
    
    >>> fmtester = FullMappingTester(TestMappingUpdate)
    >>> fmtester.test_update()

``__delitem__``::

    >>> fmtester.test___delitem__()
    Traceback (most recent call last):
      ...
    AttributeError: __delitem__
    
    >>> class TestMappingDelItem(TestMappingUpdate):
    ...     def __delitem__(self, key):
    ...         del self.data[key]
    
    >>> fmtester = FullMappingTester(TestMappingDelItem,
    ...                              include_node_checks=False)
    >>> fmtester.test___delitem__()
    Traceback (most recent call last):
      ...
    Exception: KeyError, expected ``bar``
    
    >>> fmtester.test___setitem__()
    >>> fmtester.test___delitem__()
    Traceback (most recent call last):
      ...
    Exception: Expected 2-length result. Got ``1``
    
    >>> fmtester.test___setitem__()
    >>> fmtester.test_update()
    >>> fmtester.test___delitem__()

``copy``::

    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingDelItem' object has no attribute 'copy'
    
    >>> class TestMappingCopy(TestMappingDelItem):
    ...     def copy(self):
    ...         return self
    
    >>> fmtester = FullMappingTester(TestMappingCopy,
    ...                              include_node_checks=False)
    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    Exception: ``copied`` is ``context``
    
    >>> class TestMappingCopy(TestMappingDelItem):
    ...     def copy(self):
    ...         return self.__class__()
    
    >>> fmtester = FullMappingTester(TestMappingCopy,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    KeyError: 'foo'
    
    >>> class TestMappingCopy(TestMappingDelItem):
    ...     def copy(self):
    ...         new = self.__class__()
    ...         new.update([('foo', object())])
    ...         return new
    
    >>> fmtester = FullMappingTester(TestMappingCopy,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    Exception: ``copied['foo']`` is not ``context['foo']``
    
    >>> class TestMappingCopy(TestMappingDelItem):
    ...     def copy(self):
    ...         new = self.__class__()
    ...         new.update(self.items())
    ...         return new
    
    >>> fmtester = FullMappingTester(TestMappingCopy,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_copy()
    
    >>> class TestNodeCopy(TestNodeSetItem, TestMappingCopy):
    ...     pass
    
    >>> fmtester = FullMappingTester(TestNodeCopy)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    Exception: __name__ of copied does not match
    
    >>> class TestNodeCopy(TestNodeSetItem, TestMappingCopy):
    ...     def copy(self):
    ...         new = self.__class__()
    ...         new.__name__ = self.__name__
    ...         new.update(self.items())
    ...         return new
    
    >>> fmtester = FullMappingTester(TestNodeCopy)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_copy()
    Traceback (most recent call last):
      ...
    Exception: __parent__ of copied does not match
    
    >>> class TestNodeCopy(TestNodeSetItem, TestMappingCopy):
    ...     def copy(self):
    ...         new = self.__class__()
    ...         new.__name__ = self.__name__
    ...         new.__parent__ = self.__parent__
    ...         new.update(self.items())
    ...         return new

``setdefault``::

    >>> fmtester.test_setdefault()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestNodeCopy' object has no attribute 'setdefault'
    
    >>> class TestMappingSetDefault(TestMappingCopy):
    ...     def setdefault(self, key, value=None):
    ...         return value
    
    >>> fmtester = FullMappingTester(TestMappingSetDefault,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_setdefault()
    Traceback (most recent call last):
      ...
    Exception: Replaced already existing item.
    
    >>> class TestMappingSetDefault(TestMappingCopy):
    ...     def setdefault(self, key, value=None):
    ...         self[key] = object()
    ...         return self[key]
    
    >>> fmtester = FullMappingTester(TestMappingSetDefault,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_setdefault()
    Traceback (most recent call last):
      ...
    Exception: Inserted item not same instance.
    
    >>> class TestMappingSetDefault(TestMappingCopy):
    ...     def setdefault(self, key, value=None):
    ...         try:
    ...             return self[key]
    ...         except KeyError:
    ...             self[key] = value
    ...             return value
    
    >>> fmtester = FullMappingTester(TestMappingSetDefault,
    ...                              include_node_checks=False)
    >>> fmtester.context['foo'] = TestMappingSetDefault()
    >>> fmtester.context['baz'] = TestMappingSetDefault()
    >>> fmtester.test_setdefault()

``pop``::

    >>> fmtester.test_pop()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingSetDefault' object has no attribute 'pop'
    
    >>> class TestMappingPop(TestMappingSetDefault):
    ...     def pop(self, key, default=None):
    ...         return object()
    
    >>> fmtester = FullMappingTester(TestMappingPop,
    ...                              include_node_checks=False)
    >>> fmtester.test_pop()
    Traceback (most recent call last):
      ...
    Exception: Expected ``KeyError`` for inexistent item.
    
    >>> class TestMappingPop(TestMappingSetDefault):
    ...     def pop(self, key, default=None):
    ...         if default is not None:
    ...             return object()
    ...         raise KeyError
    
    >>> fmtester = FullMappingTester(TestMappingPop,
    ...                              include_node_checks=False)
    >>> fmtester.test_pop()
    Traceback (most recent call last):
      ...
    Exception: Returned default is not same instance
    
    >>> class TestMappingPop(TestMappingSetDefault):
    ...     def pop(self, key, default=None):
    ...         if key == 'foo':
    ...             return object()
    ...         if default is not None:
    ...             return default
    ...         raise KeyError
    
    >>> fmtester = FullMappingTester(TestMappingPop,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_pop()
    Traceback (most recent call last):
      ...
    Exception: Popped item not same instance
    
    >>> class TestMappingPop(TestMappingSetDefault):
    ...     def pop(self, key, default=None):
    ...         if key == 'foo':
    ...             return self.data['foo']
    ...         if default is not None:
    ...             return default
    ...         raise KeyError
    
    >>> fmtester = FullMappingTester(TestMappingPop,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_pop()
    Traceback (most recent call last):
      ...
    Exception: Invalid mapping length after ``pop``
    
    >>> class TestMappingPop(TestMappingSetDefault):
    ...     def pop(self, key, default=None):
    ...         if default is not None:
    ...             return self.data.pop(key, default)
    ...         return self.data.pop(key)
    
    >>> fmtester = FullMappingTester(TestMappingPop,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.context['baz'] = TestMappingSetDefault()
    >>> fmtester.test_pop()

``popitem``::

    >>> fmtester.test_popitem()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingPop' object has no attribute 'popitem'
    
    >>> class TestMappingPopItem(TestMappingPop):
    ...     def popitem(self):
    ...          return
    
    >>> fmtester = FullMappingTester(TestMappingPopItem,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_popitem()
    Traceback (most recent call last):
      ...
    Exception: Expected 1-length result. Got ``2``
    
    >>> class TestMappingPopItem(TestMappingPop):
    ...     def popitem(self):
    ...          try:
    ...              return self.data.popitem()
    ...          except Exception:
    ...              pass
    
    >>> fmtester = FullMappingTester(TestMappingPopItem,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_popitem()
    Traceback (most recent call last):
      ...
    Exception: Expected ``KeyError`` when called on empty mapping
    
    >>> class TestMappingPopItem(TestMappingPop):
    ...     def popitem(self):
    ...          return self.data.popitem()
    
    >>> fmtester = FullMappingTester(TestMappingPopItem,
    ...                              include_node_checks=False)
    >>> fmtester.test___setitem__()
    >>> fmtester.test_popitem()

``clear``::

    >>> fmtester.test_clear()
    Traceback (most recent call last):
      ...
    AttributeError: 'TestMappingPopItem' object has no attribute 'clear'
    
    >>> class TestMappingClear(TestMappingPopItem):
    ...     def clear(self):
    ...          pass
    
    >>> fmtester = FullMappingTester(TestMappingClear,
    ...                              include_node_checks=False)
    >>> fmtester.test_clear()
    Traceback (most recent call last):
      ...
    Exception: Expected 0-length result. Got ``2``
    
    >>> class TestMappingClear(TestMappingPopItem):
    ...     def clear(self):
    ...          self.data.clear()
    
    >>> fmtester = FullMappingTester(TestMappingClear,
    ...                              include_node_checks=False)
    >>> fmtester.test_clear()

Run tester on mapping::

    >>> class TestMappingAll(TestMappingClear): pass
    >>> fmtester = FullMappingTester(TestMappingAll,
    ...                              include_node_checks=False)
    >>> fmtester.run()
    >>> fmtester.combined
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

Run tester on node::

    >>> class TestNodeAll(TestNodeCopy, TestMappingAll): pass
    >>> fmtester = FullMappingTester(TestNodeAll)
    >>> fmtester.run()
    >>> fmtester.combined
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

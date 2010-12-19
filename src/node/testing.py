from odict import odict

class Writer(object):
    
    def __init__(self, name, result):
        self.name = name
        self.result = result
    
    def success(self):
        self.result[self.name] = 'OK'
    
    def failed(self, msg):
        self.result[self.name] = 'Failed: %s' % (msg,)


class ContractError(Exception):
    pass


class BaseTester(object):
    
    iface_contract = []
    
    def __init__(self, class_):
        self.class_ = class_
        self.context = class_()
        self.tested = odict()
    
    def create_tree(class_):
        class_ = self.class_
        root = class_()
        for i in range(3):
            root['child_%i' % i] = class_()
            for j in range(2):
                root['child_%i' % i]['subchild_%i' % j] = class_()
        return root
    
    def combined_results(self):
        for key, val in self.tested.iteritems():
            print '``%s``: %s' % (key, self.tested[key])
    
    def writer(self, key):
        return Writer(key, self.tested)
    
    def run(self):
        for name in self.iface_contract:
            func = getattr(self, 'test_%s' % name, None)
            if func is None:
                msg = 'Given Implementation does not provide ``%s``' % name
                raise ContractError(msg)
            writer = self.writer(name)
            try:
                func()
                writer.success()
            except Exception, e:
                writer.failed(str(e))


class FullMappingTester(BaseTester):
    """Test object against ``zope.interface.mapping.IFullMaping`` interface.
    """
    
    iface_contract = [
        '__setitem__',
        '__getitem__',
        'get',
        '__iter__',
        'keys',
        'iterkeys',
        'values',
        'itervalues',
        'items',
        'iteritems',
        '__contains__',
        'has_key',
        '__len__',
        'update',
        '__delitem__',
        'copy',
        'setdefault',
    ]
    
    _object_repr_pattern = "<%s object '%s' at ...>"
    
    def _object_repr(self, key):
        return self._object_repr_pattern % (self.class_.__name__, key)
    
    def _object_repr_valid(self, context, key):
        search = self._object_repr(key).strip('...>')
        if str(context).startswith(search):
            return True
        return False
    
    def test___setitem__(self):
        """Note if __name__ is set on added node, it gets overwritten by new key
        """
        self.context['foo'] = self.class_()
        self.context['bar'] = self.class_(name='xxx')
    
    def test___getitem__(self):
        if not self._object_repr_valid(self.context['foo'], 'foo'):
            raise Exception(self._object_repr('foo'))
        if self.context['bar'].__name__ != 'bar':
            raise Exception('Child ``bar`` has wrong ``__name__``')
    
    def test_get(self):
        if not self._object_repr_valid(self.context['bar'], 'bar'):
            raise Exception(self._object_repr('bar'))
        default = object()
        if not self.context.get('xxx', default) is default:
            raise Exception('Does not return ``default`` as expected')
    
    def _check_keys(self, keys, expected):
        """Used by
        - ``test__iter__``
        - ``test_keys``
        - ``test_iterkeys``
        """
        for key in expected:
            if not key in expected:
                msg = 'Expected ``%s`` as keys. Got ``%s``'
                msg = msg  % (str(keys), str(expected))
                raise Exception(msg)
    
    def test___iter__(self):
        keys = [key for key in self.context]
        self._check_keys(keys, ['foo', 'bar'])
    
    def test_keys(self):
        keys = self.context.keys()
        self._check_keys(keys, ['foo', 'bar'])
    
    def test_iterkeys(self):
        keys = [key for key in self.context.iterkeys()]
        self._check_keys(keys, ['foo', 'bar'])
    
    def _check_values(self, values, expected):
        """Used by:
        - ``test_values``
        - ``test_itervalues``
        """
        if len(values) != len(expected):
            msg = 'Expected %i-length result. Got ``%i``'
            msg = msg % (len(expected), len(values))
            raise Exception(msg)
        for value in values:
            if not value.__name__ in expected:
                msg = 'Expected values with __name__ foo and bar. Got ``%s``'
                mgs = msg % value.__name__
                raise Exception(msg)
    
    def test_values(self):
        values = self.context.values()
        self._check_values(values, ['foo', 'bar'])
    
    def test_itervalues(self):
        values = [val for val in self.context.itervalues()]
        self._check_values(values, ['foo', 'bar'])
    
    def _check_items(self, items, expected):
        """Used by:
        - ``test_items``
        - ``test_iteritems``
        - ``test_copy``
        """
        if len(items) != len(expected):
            msg = 'Expected %i-length result. Got ``%i``'
            msg = msg % (len(expected), len(items))
            raise Exception(msg)
        for key, value in items:
            if not key in expected:
                msg = 'Expected keys ``%s``. Got ``%s``' % (str(expected), key)
                raise Exception(msg)
            if not key == value.__name__:
                msg = 'Expected same value for ``key`` and  ``__name__``'
                raise Exception(msg)
            if not self._object_repr_valid(value, key):
                raise Exception(self._object_repr(key))
    
    def test_items(self):
        self._check_items(self.context.items(), ['foo', 'bar'])
    
    def test_iteritems(self):
        items = [item for item in self.context.iteritems()]
        self._check_items(items, ['foo', 'bar'])
    
    def test___contains__(self):
        if not 'foo' in self.context or not 'bar' in self.context:
            msg = 'Expected ``foo`` and ``bar`` return ``True`` from ' + \
                  '``__contains__``'
            raise Exception(msg)
    
    def test_has_key(self):
        if not self.context.has_key('foo') \
          or not self.context.has_key('bar'):
            msg = 'Expected ``foo`` and ``bar`` return ``True`` from ' + \
                  '``has_key``'
            raise Exception(msg)
    
    def test___len__(self):
        count = len(self.context)
        if count != 2:
            raise Exception('Expected 2-length result. Got ``%i``' % count)
    
    def test_update(self):
        self.context.update((('baz', self.class_()),))
        if not self._object_repr_valid(self.context['baz'], 'baz'):
            raise Exception(self._object_repr('baz'))
    
    def test___delitem__(self):
        del self.context['bar']
        keys = self.context.keys()
        keys.sort()
        if not str(keys) == "['baz', 'foo']":
            raise Exception(str(keys))
    
    def test_copy(self):
        copied = self.context.copy()
        if not self._object_repr_valid(copied, 'None'):
            raise Exception(self._object_repr('None'))
        if copied is self.context:
            raise Exception('``copied`` is ``context``')
        self._check_items(self.context.items(), ['foo', 'baz'])
        if not copied['foo'] is self.context['foo']:
            raise Exception("``copied['foo']`` is not ``context['foo']``")
    
    def test_setdefault(self):
        """
        >>> mynew = MyNode()
        >>> mynode.setdefault('foo', mynew) is mynew
        False
        
        >>> mynode.setdefault('bar', mynew) is mynew
        True
        
        >>> mynode.items()
        [('foo', <MyNode object 'foo' at ...>), 
        ('baz', <MyNode object 'baz' at ...>), 
        ('bar', <MyNode object 'bar' at ...>)]
        """

class LocationTester(BaseTester):
    """Test object against ``zope.location.interfaces.ILocation`` interface.
    """

class NodeTester(BaseTester):
    """Test object against ``node.interfaces.INode`` interface.
    """
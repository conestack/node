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
                func(writer)
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
    
    def test___setitem__(self, writer):
        """Note if __name__ is set on added node, it gets overwritten by new key
        """
        self.context['foo'] = self.class_()
        self.context['bar'] = self.class_(name='xxx')
        writer.success()
    
    def test___getitem__(self, writer):
        if not self._object_repr_valid(self.context['foo'], 'foo'):
            writer.failed(self._object_repr('foo'))
            return
        if self.context['bar'].__name__ != 'bar':
            writer.failed('Child ``bar`` has wrong ``__name__``')
            return
        writer.success()
    
    def test_get(self, writer):
        if not self._object_repr_valid(self.context['bar'], 'bar'):
            writer.failed(self._object_repr('bar'))
            return
        default = object()
        if not self.context.get('xxx', default) is default:
            writer.failed('Does not return ``default`` as expected')
            return
        writer.success()
    
    def _check_keys(self, writer, keys):
        """Used by
        - ``test__iter__``
        - ``test_keys``
        - ``test_iterkeys``
        """
        if not 'foo' in keys or not 'bar' in keys:
            msg = 'Expected ``foo`` and ``bar`` as keys. Got ``%s``' % str(keys)
            writer.failed(msg)
            return
        writer.success()
    
    def test___iter__(self, writer):
        keys = [key for key in self.context]
        self._check_keys(writer, keys)
    
    def test_keys(self, writer):
        keys = self.context.keys()
        self._check_keys(writer, keys)
    
    def test_iterkeys(self, writer):
        keys = [key for key in self.context.iterkeys()]
        self._check_keys(writer, keys)
    
    def _check_values(self, writer, values):
        """Used by:
        - ``test_values``
        - ``test_itervalues``
        """
        if len(values) != 2:
            writer.failed('Expected 2-length result. Got ``%i``' % len(values))
            return
        expected = ['foo', 'bar']
        for value in values:
            if not value.__name__ in expected:
                msg = 'Expected values with __name__ foo and bar. Got ``%s``'
                mgs = msg % value.__name__
                writer.failed(msg)
                return
        writer.success()
    
    def test_values(self, writer):
        values = self.context.values()
        self._check_values(writer, values)
    
    def test_itervalues(self, writer):
        values = [val for val in self.context.itervalues()]
        self._check_values(writer, values)
    
    def _check_items(self, writer, items, expected=['foo', 'bar']):
        """Used by:
        - ``test_items``
        - ``test_iteritems``
        - ``test_copy``
        """
        if len(items) != len(expected):
            msg = 'Expected %i-length result. Got ``%i``'
            msg = msg % (len(expected), len(items))
            writer.failed(msg)
            return False
        for key, value in items:
            if not key in expected:
                msg = 'Expected keys ``%s``. Got ``%s``' % (str(expected), key)
                writer.failed(msg)
                return False
            if not key == value.__name__:
                msg = 'Expected same value for ``key`` and  ``__name__``'
                writer.failed(msg)
                return False
            if not self._object_repr_valid(value, key):
                writer.failed(self._object_repr(key))
                return False
        return True
    
    def test_items(self, writer):
        if not self._check_items(writer, self.context.items(), ['foo', 'bar']):
            return
        writer.success()
    
    def test_iteritems(self, writer):
        items = [item for item in self.context.iteritems()]
        if not self._check_items(writer, items, ['foo', 'bar']):
            return
        writer.success()
    
    def test___contains__(self, writer):
        if not 'foo' in self.context or not 'bar' in self.context:
            msg = 'Expected ``foo`` and ``bar`` return ``True`` from ' + \
                  '``__contains__``'
            writer.failed(msg)
            return
        writer.success()
    
    def test_has_key(self, writer):
        if not self.context.has_key('foo') \
          or not self.context.has_key('bar'):
            msg = 'Expected ``foo`` and ``bar`` return ``True`` from ' + \
                  '``has_key``'
            writer.failed(msg)
            return
        writer.success()
    
    def test___len__(self, writer):
        count = len(self.context)
        if count != 2:
            writer.failed('Expected 2-length result. Got ``%i``' % count)
            return
        writer.success()
    
    def test_update(self, writer):
        self.context.update((('baz', self.class_()),))
        if not self._object_repr_valid(self.context['baz'], 'baz'):
            writer.failed(self._object_repr('baz'))
            return
        writer.success()
    
    def test___delitem__(self, writer):
        del self.context['bar']
        keys = self.context.keys()
        keys.sort()
        if not str(keys) == "['baz', 'foo']":
            writer.failed(str(keys))
        writer.success()
    
    def test_copy(self, writer):
        copied = self.context.copy()
        if not self._object_repr_valid(copied, 'None'):
            writer.failed(self._object_repr('None'))
            return
        if copied is self.context:
            writer.failed('``copied`` is ``context``')
            return
        if not self._check_items(writer, self.context.items(), ['foo', 'baz']):
            return
        if not copied['foo'] is self.context['foo']:
            writer.failed("``copied['foo']`` is not ``context['foo']``")
            return
        writer.success()
    
    def test_setdefault(self, writer):
        """
        """
        writer.success()

class LocationTester(BaseTester):
    """Test object against ``zope.location.interfaces.ILocation`` interface.
    """

class NodeTester(BaseTester):
    """Test object against ``node.interfaces.INode`` interface.
    """
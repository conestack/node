from odict import odict
from node.interfaces import INode


def create_tree(class_):
        root = class_()
        for i in range(3):
            root['child_%i' % i] = class_()
            for j in range(2):
                root['child_%i' % i]['subchild_%i' % j] = class_()
        return root


class ResultWriter(object):
    
    def __init__(self, results, name=None):
        self.name = name
        self.results = results
    
    def success(self):
        self.results[self.name] = 'OK'
    
    def failed(self, msg):
        self.results[self.name] = 'Failed: %s' % (msg,)
    
    def print_combined(self):
        for key, val in self.results.iteritems():
            print '``%s``: %s' % (key, self.results[key])


class ContractError(Exception):
    pass


class BaseTester(object):
    
    # list of interface contract attributes to test.
    # test functions always are named 'test_[contractname]'.
    # execution is in order, so you might depend tests to prior happened
    # context manipulation.
    iface_contract = []
    
    def __init__(self, class_, context=None):
        """
        ``class_``
            class object for creating children in test.
        ``context``
            an optional root context to test against, If None, an instance of 
            class_ is created as root.
        """
        self._results = odict()
        self.class_ = class_
        self.context = context
        if self.context is None:
            self.context = class_()
        self._results = odict()
    
    @property
    def results(self):
        return self._results
    
    @property
    def combined(self):
        self.writer().print_combined()
    
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
    
    def writer(self, key=None):
        return ResultWriter(self._results, name=key)


class FullMappingTester(BaseTester):
    """Test node against ``zope.interface.mapping.IFullMaping`` interface.
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
        'pop',
        'popitem',
        'clear',
    ]
    
    def __init__(self, class_, context=None, include_node_checks=True):
        super(FullMappingTester, self).__init__(class_, context=context)
        self.include_node_checks = include_node_checks
    
    def test___setitem__(self):
        self.context['foo'] = self.class_()
        if self.include_node_checks:
            self.context['bar'] = self.class_(name='xxx')
        else:
            self.context['bar'] = self.class_()
    
    def test___getitem__(self):
        child = self.context['foo']
        if self.include_node_checks:
            if self.context['bar'].__name__ != 'bar':
                raise Exception('Child ``bar`` has wrong ``__name__``')
    
    def test_get(self):
        default = object()
        if self.context.get('foo', default) is default:
            raise Exception('Expected value, got default')
        value = self.context.get('xxx', default)
        if not value is default:
            raise Exception('Expected default, got %s' % str(value))
    
    def _check_keys(self, keys, expected):
        if len(keys) != len(expected):
            msg = 'Expected %i-length result. Got ``%i``'
            msg = msg % (len(expected), len(keys))
            raise Exception(msg)
        for key in keys:
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
        if len(values) != len(expected):
            msg = 'Expected %i-length result. Got ``%i``'
            msg = msg % (len(expected), len(values))
            raise Exception(msg)
        if self.include_node_checks:
            for value in values:
                if not value.__name__ in expected:
                    msg = 'Expected __name__ of value invalid. Got ``%s``'
                    raise Exception(msg % value.__name__)
    
    def test_values(self):
        values = self.context.values()
        self._check_values(values, ['foo', 'bar'])
    
    def test_itervalues(self):
        values = [val for val in self.context.itervalues()]
        self._check_values(values, ['foo', 'bar'])
    
    def _check_items(self, items, expected):
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
        new = self.class_()
        if self.context.setdefault('foo', new) is new:
            raise Exception('Replaced already existing item.')
        if not self.context.setdefault('bar', new) is new:
            raise Exception('Inserted item not same instance.')
        self._check_items(self.context.items(), ['foo', 'bar', 'baz'])
    
    def test_pop(self):
        try:
            self.context.pop('xxx')
            raise Exception('Excected ``KeyError`` for inexistent item.')
        except KeyError:
            pass
        default = object()
        if not self.context.pop('xxx', default) is default:
            raise Exception('Returned default is not same instance')
        popped = self.context.pop('foo')
        if not self._object_repr_valid(popped, 'foo'):
            raise Exception('Expected ``foo``, got ``%s``' % popped.__name__)
        self._check_keys(self.context.keys(), ['baz', 'bar'])
    
    def test_popitem(self):
        self.context.popitem()
        count = len(self.context.keys())
        if count != 1:
            msg = 'Expected 1-length result. Got ``%i``' % count
            raise Exception(msg)
        self.context.popitem()
        try:
            self.context.popitem()
            msg = 'Expected ``KeyError`` when called on empty mapping'
            raise Exception(msg)
        except KeyError:
            pass
    
    def test_clear(self):
        self.context['foo'] = self.class_()
        self.context['bar'] = self.class_()
        self._check_keys(self.context.keys(), ['foo', 'bar'])
        self.context.clear()
        self._check_keys(self.context.keys(), [])


class LocationTester(BaseTester):
    """Test object against ``zope.location.interfaces.ILocation`` interface.
    """


class NodeTester(BaseTester):
    """Test object against ``node.interfaces.INode`` interface.
    """

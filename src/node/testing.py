from odict import odict

class Writer(object):
    
    def __init__(self, name, result):
        self.name = name
        self.result = result
    
    def success(self):
        self.result[self.name] = 'OK'
    
    def failed(self, msg):
        self.result[self.name] = 'Failed: %s' % (message,)


class ContractViolation(Exception):
    pass


class BaseTester(object):
    
    iface_contracts = list()
    
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
        for contract in self.iface_contracts:
            func = getattr(self, 'test_%s' % contract, None)
            if func is None:
                msg = u"Given implementation does not provide ``%s``" % contract
                raise ContractViolation(msg)
            func()


class FullMappingTester(BaseTester):
    """Test object against ``zope.interface.mapping.IFullMaping`` interface.
    """
    
    iface_contracts = [
        '__setitem__',
        '__getitem__',
        'get',
        '__iter__',
        'keys',
        'iterkeys',
        'values',
        'itervalues',
        'items',
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
        writer = self.writer('__setitem__')
        try:
            self.context['foo'] = self.class_()
            self.context['bar'] = self.class_(name='xxx')
            writer.success()
        except Exception, e:
            writer.failed(str(e))
    
    def test___getitem__(self):
        writer = self.writer('__getitem__')
        try:
            if not self._object_repr_valid(self.context['foo'], 'foo'):
                writer.failed(self._object_repr('foo'))
                return
            if self.context['bar'].__name__ != 'bar':
                writer.failed('Child ``bar`` has wrong ``__name__``')
                return
            writer.success()
        except Exception, e:
            writer.failed(str(e))
    
    def test_get(self):
        writer = self.writer('get')
        try:
            if not self._object_repr_valid(self.context['bar'], 'bar'):
                writer.failed(self._object_repr('bar'))
                return
            default = object()
            if not self.context.get('xxx', default) is default:
                writer.failed('Does not return ``default`` as expected')
                return
            writer.success()
        except Exception, e:
            writer.failed(str(e))
    
    def _check_keys(self, writer, keys):
        """Used by
        - ``_test__iter__``
        - ``_test_keys``
        - ``_test_iterkeys``
        """
        if not 'foo' in keys or not 'bar' in keys:
            writer.failed('Expected ``foo`` and ``bar`` as keys.')
            return
        writer.success()
    
    def test___iter__(self):
        writer = self.writer('__iter__')
        try:
            keys = [key for key in self.context]
            self._check_keys(writer, keys)
        except Exception, e:
            writer.failed(str(e))
    
    def test_keys(self):
        writer = self.writer('keys')
        try:
            keys = self.context.keys()
            self._check_keys(writer, keys)
        except Exception, e:
            writer.failed(str(e))
    
    def test_iterkeys(self):
        writer = self.writer('iterkeys')
        try:
            keys = [key for key in self.context.iterkeys()]
            self._check_keys(writer, keys)
        except Exception, e:
            writer.failed(str(e))
    
    def _check_values(self, writer, values):
        """Used by:
        - ``_test_values``
        - ``_test_itervalues``
        """
        if len(values) != 2:
            writer.failed('Expected 2-length result. Got %i' % len(values))
            return
        expected = ['foo', 'bar']
        for value in values:
            if not value.__name__ in expected:
                msg = 'Expected values with __name__ foo and bar. Got %s'
                mgs = msg % value.__name__
                writer.failed(msg)
                return
        writer.success()
    
    def test_values(self):
        writer = self.writer('values')
        try:
            values = self.context.values()
            self._check_values(writer, values)
        except Exception, e:
            writer.failed(str(e))
    
    def test_itervalues(self):
        writer = self.writer('itervalues')
        try:
            values = [val for val in self.context.itervalues()]
            self._check_values(writer, values)
        except Exception, e:
            writer.failed(str(e))
    
    def test_items(self):
        """
        """

class LocationTester(BaseTester):
    """Test object against ``zope.location.interfaces.ILocation`` interface.
    """

class NodeTester(BaseTester):
    """Test object against ``node.interfaces.INode`` interface.
    """
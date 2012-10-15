from base import BaseTester


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
                msg = msg % (str(keys), str(expected))
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
            if self.include_node_checks:
                if key != value.__name__:
                    msg = 'Expected same value for ``key`` "%s" and ' + \
                          '``__name__`` "%s"'
                    msg = msg % (str(key), str(value.__name__))
                    raise Exception(msg)
        for key, value in items:
            if not value is self.context[key]:
                msg = 'Expected %s, got %s' % (str(value),
                                               str(self.context[key]))
                raise Exception(msg)

    def test_items(self):
        self._check_items(self.context.items(), ['foo', 'bar'])

    def test_iteritems(self):
        items = [item for item in self.context.iteritems()]
        self._check_items(items, ['foo', 'bar'])

    def test___contains__(self):
        if not 'foo' in self.context or not 'bar' in self.context:
            msg = 'Expected ``foo`` and ``bar`` return ``True`` by ' + \
                  '``__contains__``'
            raise Exception(msg)
        if 'xxx' in self.context:
            msg = 'Expected __contains__ to return False for non-existent key'
            raise Exception(msg)

    def test_has_key(self):
        if not self.context.has_key('foo') \
          or not self.context.has_key('bar'):
            msg = 'Expected ``foo`` and ``bar`` return ``True`` by ' + \
                  '``has_key``'
            raise Exception(msg)

    def test___len__(self):
        count = len(self.context)
        if count != 2:
            raise Exception('Expected 2-length result. Got ``%i``' % count)

    def test_update(self):
        baz = self.class_()
        blub = self.class_()
        # if update maps to odict update, kw's fail
        self.context.update(baz)
        self.context.update((('baz', baz),), blub=blub)
        #self.context.update((('baz', baz), ('blub', blub)))
        try:
            self.context['baz']
            self.context['blub']
        except KeyError:
            raise Exception('KeyError, Expected ``baz`` and ``blub`` after '
                            'update')
        if baz is not self.context['baz']:
            raise Exception('Object at ``baz`` not expected one after update')
        if blub is not self.context['blub']:
            raise Exception('Object at ``blub`` not expected one after update')
        try:
            del self.context['blub']
        except:
            try:
                del self.context.data['blub']
            except:
                raise RuntimeError("Cannot del test key.")
        try:
            self.context.update(dict(), dict())
            raise Exception('Expected TypeError for update with more than one '
                            'positional argument.')
        except TypeError:
            pass

    def test___delitem__(self):
        try:
            del self.context['bar']
        except KeyError:
            raise Exception('KeyError, expected ``bar``')
        self._check_keys(self.context.keys(), ['baz', 'foo'])

    def test_copy(self):
        PARENT_MARKER = object()
        if self.include_node_checks:
            old_name = self.context.__name__
            old_parent = self.context.__parent__
            self.context.__name__ = 'nametopcopy'
            self.context.__parent__ = PARENT_MARKER
        copied = self.context.copy()
        if copied is self.context:
            raise Exception('``copied`` is ``context``')
        if not copied['foo'] is self.context['foo']:
            raise Exception("``copied['foo']`` is not ``context['foo']``")
        if self.include_node_checks:
            if copied.__name__ != self.context.__name__:
                raise Exception('__name__ of copied does not match')
            if not copied.__parent__ is self.context.__parent__:
                raise Exception('__parent__ of copied does not match')
            self.context.__name__ = old_name
            self.context.__parent__ = old_parent

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
            raise Exception('Expected ``KeyError`` for inexistent item.')
        except KeyError:
            pass
        default = object()
        if not self.context.pop('xxx', default) is default:
            raise Exception('Returned default is not same instance')
        originlen = len(self.context)
        topop = self.context['foo']
        popped = self.context.pop('foo')
        afterlen = len(self.context)
        if topop is not popped:
            raise Exception('Popped item not same instance')
        if afterlen != originlen - 1:
            raise Exception('Invalid mapping length after ``pop``')
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

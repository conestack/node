from node.testing import FullMappingTester
import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


IS_PY2 = sys.version_info[0] < 3
IS_PYPY = '__pypy__' in sys.builtin_module_names


###############################################################################
# Mock objects
###############################################################################

class TestMapping(object):
    def __init__(self):
        self.data = dict()


class TestNode(TestMapping):
    def __init__(self, name=None, parent=None):
        super(TestNode, self).__init__()
        self.__name__ = name
        self.__parent__ = parent


###############################################################################
# Tests
###############################################################################

class TestFullmapping(unittest.TestCase):

    def except_error(self, exc, func, *args, **kw):
        try:
            func(*args, **kw)
        except exc as e:
            return e
        else:
            raise Exception(
                'Expected \'{}\' when calling \'{}\''.format(exc, func)
            )

    def test___setitem__(self):
        fmtester = FullMappingTester(TestMapping)
        err = self.except_error(TypeError, fmtester.test___setitem__)
        self.assertEqual(
            str(err),
            '\'TestMapping\' object does not support item assignment'
        )

        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        fmtester = FullMappingTester(TestMappingSetItem)
        err = self.except_error(TypeError, fmtester.test___setitem__)
        self.assertEqual(
            str(err),
            '__init__() got an unexpected keyword argument \'name\''
        )

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            pass

        fmtester = FullMappingTester(TestNodeSetItem)
        fmtester.test___setitem__()

    def test___getitem__(self):
        fmtester = FullMappingTester(TestMapping)
        # Python 2: 'TestMapping' object has no attribute '__getitem__'
        # Python 3: 'TestMapping' object is not subscriptable
        err = self.except_error(TypeError, fmtester.test___getitem__)
        self.assertTrue(str(err).startswith('\'TestMapping\' object'))

        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        fmtester = FullMappingTester(TestMappingGetItem)
        fmtester.context['foo'] = TestMappingGetItem()
        fmtester.context['bar'] = TestMappingGetItem()
        err = self.except_error(AttributeError, fmtester.test___getitem__)
        self.assertEqual(
            str(err),
            '\'TestMappingGetItem\' object has no attribute \'__name__\''
        )

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            pass

        class TestNodeGetItem(TestNodeSetItem, TestMappingGetItem):
            pass

        fmtester = FullMappingTester(TestNodeGetItem)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___getitem__)
        self.assertEqual(
            str(err),
            'Child ``bar`` has wrong ``__name__``'
        )

        class TestNodeSetItem(TestNodeSetItem):
            def __setitem__(self, name, value):
                value.__parent__ = self
                value.__name__ = name
                self.data[name] = value

        class TestNodeGetItem(TestNodeSetItem, TestMappingGetItem):
            pass

        fmtester = FullMappingTester(TestNodeGetItem)
        fmtester.test___setitem__()
        fmtester.test___getitem__()

    def test_get(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            def __setitem__(self, name, value):
                value.__parent__ = self
                value.__name__ = name
                self.data[name] = value

        class TestNodeGetItem(TestNodeSetItem, TestMappingGetItem):
            pass

        fmtester = FullMappingTester(TestNodeGetItem)
        err = self.except_error(AttributeError, fmtester.test_get)
        self.assertEqual(
            str(err),
            '\'TestNodeGetItem\' object has no attribute \'get\''
        )

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return object()

        fmtester = FullMappingTester(
            TestMappingGet,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_get)
        self.assertTrue(
            str(err).startswith('Expected default, got <object object at')
        )

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return default

        fmtester = FullMappingTester(
            TestMappingGet,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_get)
        self.assertEqual(
            str(err),
            'Expected value, got default'
        )

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        fmtester = FullMappingTester(
            TestMappingGet,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_get()

    def test___iter__(self):
        fmtester = FullMappingTester(TestMapping)
        err = self.except_error(TypeError, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            '\'TestMapping\' object is not iterable'
        )

        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return iter(list())

        fmtester = FullMappingTester(TestMappingIter)
        err = self.except_error(Exception, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return iter(['a', 'b'])

        fmtester = FullMappingTester(TestMappingIter)
        err = self.except_error(Exception, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            'Expected ``[\'a\', \'b\']`` as keys. Got ``[\'foo\', \'bar\']``'
        )

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        fmtester = FullMappingTester(
            TestMappingIter,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___iter__()

    def test_keys(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        fmtester = FullMappingTester(
            TestMappingIter,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_keys)
        self.assertEqual(
            str(err),
            '\'TestMappingIter\' object has no attribute \'keys\''
        )

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        fmtester = FullMappingTester(
            TestMappingKeys,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_keys()

    def test_iterkeys(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        fmtester = FullMappingTester(
            TestMappingKeys,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_iterkeys)
        self.assertEqual(
            str(err),
            '\'TestMappingKeys\' object has no attribute \'iterkeys\''
        )

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        fmtester = FullMappingTester(
            TestMappingIterKeys,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_iterkeys()

    def test_values(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        fmtester = FullMappingTester(
            TestMappingIterKeys,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_values)
        self.assertEqual(
            str(err),
            '\'TestMappingIterKeys\' object has no attribute \'values\''
        )

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        fmtester = FullMappingTester(
            TestMappingValues,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_values)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        fmtester.test___setitem__()
        fmtester.test_values()

        fmtester = FullMappingTester(TestMappingValues)
        fmtester.context['foo'] = TestMappingValues()
        fmtester.context['bar'] = TestMappingValues()

        err = self.except_error(AttributeError, fmtester.test_values)
        self.assertEqual(
            str(err),
            '\'TestMappingValues\' object has no attribute \'__name__\''
        )

        class TestNodeValues(TestNode, TestMappingValues):
            pass

        fmtester = FullMappingTester(TestNodeValues)
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test_values)
        self.assertEqual(
            str(err),
            'Expected __name__ of value invalid. Got ``None``'
        )

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            def __setitem__(self, name, value):
                value.__parent__ = self
                value.__name__ = name
                self.data[name] = value

        class TestNodeValues(TestNodeSetItem, TestMappingValues):
            pass

        fmtester = FullMappingTester(TestNodeValues)
        fmtester.test___setitem__()
        fmtester.test_values()

    def test_itervalues(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            def __setitem__(self, name, value):
                value.__parent__ = self
                value.__name__ = name
                self.data[name] = value

        class TestNodeValues(TestNodeSetItem, TestMappingValues):
            pass

        fmtester = FullMappingTester(TestNodeValues)
        err = self.except_error(AttributeError, fmtester.test_itervalues)
        self.assertEqual(
            str(err),
            '\'TestNodeValues\' object has no attribute \'itervalues\''
        )

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        fmtester = FullMappingTester(
            TestMappingIterValues,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_itervalues()

    def test_items(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        fmtester = FullMappingTester(
            TestMappingIterValues,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_items)
        self.assertEqual(
            str(err),
            '\'TestMappingIterValues\' object has no attribute \'items\''
        )

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return list()

        fmtester = FullMappingTester(
            TestMappingItems,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return [('foo', object()), ('b', object())]

        fmtester = FullMappingTester(
            TestMappingItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected keys ``[\'foo\', \'bar\']``. Got ``b``'
        )

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return [('foo', object()), ('bar', object())]

        fmtester = FullMappingTester(
            TestMappingItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test_items)
        self.assertTrue(str(err).find('Expected <object object at') > -1)
        self.assertTrue(str(err).find('got <node.', 26) > -1)
        self.assertTrue(str(err).find('TestMappingItems object at', 38) > -1)

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return self.data.items()

        fmtester = FullMappingTester(
            TestMappingItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_items()

        class TestNodeItems(TestNode, TestMappingItems):
            pass

        fmtester = FullMappingTester(TestNodeItems)
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected same value for ``key`` "foo" and ``__name__`` "None"'
        )

        class TestNodeSetItem(TestNode, TestMappingSetItem):
            def __setitem__(self, name, value):
                value.__parent__ = self
                value.__name__ = name
                self.data[name] = value

        class TestNodeItems(TestNodeSetItem, TestMappingItems):
            pass

        fmtester = FullMappingTester(TestNodeItems)
        fmtester.test___setitem__()
        fmtester.test_items()

    def test_iteritems(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return self.data.items()

        fmtester = FullMappingTester(TestMappingItems)
        err = self.except_error(AttributeError, fmtester.test_iteritems)
        self.assertEqual(
            str(err),
            '\'TestMappingItems\' object has no attribute \'iteritems\''
        )

        class TestMappingIterItems(TestMappingItems):
            def iteritems(self):
                return iter(self.data.items())

        fmtester = FullMappingTester(
            TestMappingIterItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_iteritems()

    def test___contains__(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return self.data.items()

        class TestMappingIterItems(TestMappingItems):
            def iteritems(self):
                return iter(self.data.items())

        class TestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return False

        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``__contains__``'
        )

        class TestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return True

        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected __contains__ to return False for non-existent key'
        )

        class TestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return key in self.data

        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___contains__()

    def test_has_key(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return self.data.items()

        class TestMappingIterItems(TestMappingItems):
            def iteritems(self):
                return iter(self.data.items())

        class TestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return key in self.data

        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            '\'TestMappingContains\' object has no attribute \'has_key\''
        )

        class TestMappingHasKey(TestMappingContains):
            def has_key(self, key):
                return False

        fmtester = FullMappingTester(
            TestMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``has_key``'
        )

        class TestMappingHasKey(TestMappingContains):
            def has_key(self, key):
                if IS_PY2:
                    return self.data.has_key(key)
                return key in self.data

        fmtester = FullMappingTester(
            TestMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_has_key()

    def test___len__(self):
        class TestMappingSetItem(TestMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        class TestMappingGetItem(TestMappingSetItem):
            def __getitem__(self, key):
                return self.data[key]

        class TestMappingGet(TestMappingGetItem):
            def get(self, key, default=None):
                return self.data.get(key, default)

        class TestMappingIter(TestMappingGet):
            def __iter__(self):
                return self.data.__iter__()

        class TestMappingKeys(TestMappingIter):
            def keys(self):
                return [k for k in self.data]

        class TestMappingIterKeys(TestMappingKeys):
            def iterkeys(self):
                return self.data.__iter__()

        class TestMappingValues(TestMappingIterKeys):
            def values(self):
                return self.data.values()

        class TestMappingIterValues(TestMappingValues):
            def itervalues(self):
                return iter(self.data.values())

        class TestMappingItems(TestMappingIterValues):
            def items(self):
                return self.data.items()

        class TestMappingIterItems(TestMappingItems):
            def iteritems(self):
                return iter(self.data.items())

        class TestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return key in self.data

        class TestMappingHasKey(TestMappingContains):
            def has_key(self, key):
                if IS_PY2:
                    return self.data.has_key(key)
                return key in self.data

        fmtester = FullMappingTester(
            TestMappingHasKey,
            include_node_checks=False
        )
        expected = '\'TestMappingHasKey\' has no length' if IS_PYPY else \
            'object of type \'TestMappingHasKey\' has no len()'
        err = self.except_error(TypeError, fmtester.test___len__)
        self.assertEqual(str(err), expected)

        class TestMappingLen(TestMappingHasKey):
            def __len__(self):
                return 0

        fmtester = FullMappingTester(
            TestMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()

        err = self.except_error(Exception, fmtester.test___len__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class TestMappingLen(TestMappingHasKey):
            def __len__(self):
                return len(self.data)

        fmtester = FullMappingTester(
            TestMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___len__()

"""

update
~~~~~~

.. code-block:: pycon

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


__delitem__
~~~~~~~~~~~

.. code-block:: pycon

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


copy
~~~~

.. code-block:: pycon

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


setdefault
~~~~~~~~~~

.. code-block:: pycon

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


pop
~~~

.. code-block:: pycon

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


popitem
~~~~~~~

.. code-block:: pycon

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


clear
~~~~~

.. code-block:: pycon

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

Run tester on mapping:

.. code-block:: pycon

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

Run tester on node:

.. code-block:: pycon

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
"""


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover
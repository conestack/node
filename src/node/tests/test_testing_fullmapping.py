from node.testing import FullMappingTester
import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


IS_PY2 = sys.version_info[0] < 3
IS_PYPY = '__pypy__' in sys.builtin_module_names
ITER_FUNC = 'iteritems' if IS_PY2 else 'items'


###############################################################################
# Mock objects
###############################################################################

class TestMapping(object):
    def __init__(self):
        self.data = dict()


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
        # XXX: return self.data.has_key(key) if IS_PY2 else key in self.data
        if IS_PY2:
            return self.data.has_key(key)
        return key in self.data


class TestMappingLen(TestMappingHasKey):
    def __len__(self):
        return len(self.data)


class TestMappingUpdate(TestMappingLen):
    def update(self, data=(), **kw):
        for key, value in data:
            self[key] = value
        for key, value in getattr(kw, ITER_FUNC)():
            self[key] = value


class TestMappingDelItem(TestMappingUpdate):
    def __delitem__(self, key):
        del self.data[key]


class TestMappingCopy(TestMappingDelItem):
    def copy(self):
        new = self.__class__()
        new.update(self.items())
        return new


class TestMappingSetDefault(TestMappingCopy):
    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value


class TestMappingPop(TestMappingSetDefault):
    def pop(self, key, default=None):
        if default is not None:
            return self.data.pop(key, default)
        return self.data.pop(key)


class TestMappingPopItem(TestMappingPop):
    def popitem(self):
        return self.data.popitem()


class TestMappingClear(TestMappingPopItem):
    def clear(self):
        self.data.clear()


class TestMappingAll(TestMappingClear):
    pass


class TestNode(TestMapping):
    def __init__(self, name=None, parent=None):
        super(TestNode, self).__init__()
        self.__name__ = name
        self.__parent__ = parent


class TestNodeSetItem(TestNode, TestMappingSetItem):
    def __setitem__(self, name, value):
        value.__parent__ = self
        value.__name__ = name
        self.data[name] = value


class TestNodeItems(TestNodeSetItem, TestMappingItems):
    pass


class TestNodeCopy(TestNodeSetItem, TestMappingCopy):
    def copy(self):
        new = self.__class__()
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        new.update(self.items())
        return new


class TestNodeAll(TestNodeCopy, TestMappingAll):
    pass


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
        fmtester = FullMappingTester(
            TestMappingIterValues,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_items)
        self.assertEqual(
            str(err),
            '\'TestMappingIterValues\' object has no attribute \'items\''
        )

        class FailingTestMappingItems(TestMappingIterValues):
            def items(self):
                return list()

        fmtester = FullMappingTester(
            FailingTestMappingItems,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class FailingTestMappingItems2(TestMappingIterValues):
            def items(self):
                return [('foo', object()), ('b', object())]

        fmtester = FullMappingTester(
            FailingTestMappingItems2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected keys ``[\'foo\', \'bar\']``. Got ``b``'
        )

        class FailingTestMappingItems3(TestMappingIterValues):
            def items(self):
                return [('foo', object()), ('bar', object())]

        fmtester = FullMappingTester(
            FailingTestMappingItems3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertTrue(str(err).find('Expected <object object at') > -1)
        self.assertTrue(str(err).find('got <node.', 26) > -1)
        self.assertTrue(str(err).find('FailingTestMappingItems3', 38) > -1)

        fmtester = FullMappingTester(
            TestMappingItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_items()

        class FailingTestNodeItems(TestNode, TestMappingItems):
            pass

        fmtester = FullMappingTester(FailingTestNodeItems)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected same value for ``key`` "foo" and ``__name__`` "None"'
        )

        fmtester = FullMappingTester(TestNodeItems)
        fmtester.test___setitem__()
        fmtester.test_items()

    def test_iteritems(self):
        fmtester = FullMappingTester(TestMappingItems)
        err = self.except_error(AttributeError, fmtester.test_iteritems)
        self.assertEqual(
            str(err),
            '\'TestMappingItems\' object has no attribute \'iteritems\''
        )

        fmtester = FullMappingTester(
            TestMappingIterItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_iteritems()

    def test___contains__(self):
        class FailingTestMappingContains(TestMappingIterItems):
            def __contains__(self, key):
                return False

        fmtester = FullMappingTester(
            FailingTestMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``__contains__``'
        )

        class FailingTestMappingContains2(TestMappingIterItems):
            def __contains__(self, key):
                return True

        fmtester = FullMappingTester(
            FailingTestMappingContains2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected __contains__ to return False for non-existent key'
        )

        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___contains__()

    def test_has_key(self):
        fmtester = FullMappingTester(
            TestMappingContains,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            '\'TestMappingContains\' object has no attribute \'has_key\''
        )

        class FailingTestMappingHasKey(TestMappingContains):
            def has_key(self, key):
                return False

        fmtester = FullMappingTester(
            FailingTestMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``has_key``'
        )

        fmtester = FullMappingTester(
            TestMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_has_key()

    def test___len__(self):
        fmtester = FullMappingTester(
            TestMappingHasKey,
            include_node_checks=False
        )
        expected = '\'TestMappingHasKey\' has no length' if IS_PYPY else \
            'object of type \'TestMappingHasKey\' has no len()'
        err = self.except_error(TypeError, fmtester.test___len__)
        self.assertEqual(str(err), expected)

        class FailingTestMappingLen(TestMappingHasKey):
            def __len__(self):
                return 0

        fmtester = FullMappingTester(
            FailingTestMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___len__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        fmtester = FullMappingTester(
            TestMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___len__()

    def test_update(self):
        fmtester = FullMappingTester(
            TestMappingLen,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_update)
        self.assertEqual(
            str(err),
            '\'TestMappingLen\' object has no attribute \'update\''
        )

        class FailingTestMappingUpdate(TestMappingLen):
            def update(self, data=(), **kw):
                pass

        fmtester = FullMappingTester(FailingTestMappingUpdate)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'KeyError, Expected ``baz`` and ``blub`` after update'
        )

        class FailingTestMappingUpdate2(TestMappingLen):
            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = object()
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = object()

        fmtester = FullMappingTester(FailingTestMappingUpdate2)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Object at ``baz`` not expected one after update'
        )

        class FailingTestMappingUpdate3(TestMappingLen):
            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = object()

        fmtester = FullMappingTester(FailingTestMappingUpdate3)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Object at ``blub`` not expected one after update'
        )

        class BrokenData(dict):
            def __delitem__(self, key):
                if key == 'blub':
                    raise Exception(u"Broken implementation")

        class FailingTestMappingUpdate4(TestMappingLen):
            def __init__(self):
                self.data = BrokenData()

            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = value

        fmtester = FullMappingTester(FailingTestMappingUpdate4)
        err = self.except_error(RuntimeError, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Cannot del test key.'
        )

        class FailingTestMappingUpdate5(TestMappingLen):
            def update(self, data=(), data1=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = value

        fmtester = FullMappingTester(FailingTestMappingUpdate5)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Expected TypeError for update with more than one positional '
            'argument.'
        )

        fmtester = FullMappingTester(TestMappingUpdate)
        fmtester.test_update()

    def test___delitem__(self):
        fmtester = FullMappingTester(TestMappingUpdate)
        expected = '__delitem__' if not IS_PYPY else \
            '\'TestMappingUpdate\' object does not support item deletion'
        exc = TypeError if IS_PYPY else AttributeError
        err = self.except_error(exc, fmtester.test___delitem__)
        self.assertEqual(str(err), expected)

        fmtester = FullMappingTester(
            TestMappingDelItem,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test___delitem__)
        self.assertEqual(
            str(err),
            'KeyError, expected ``bar``'
        )

        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___delitem__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``1``'
        )

        fmtester.test___setitem__()
        fmtester.test_update()
        fmtester.test___delitem__()

    def test_copy(self):
        fmtester = FullMappingTester(
            TestMappingDelItem,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '\'TestMappingDelItem\' object has no attribute \'copy\''
        )

        class FailingTestMappingCopy(TestMappingDelItem):
            def copy(self):
                return self

        fmtester = FullMappingTester(
            FailingTestMappingCopy,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '``copied`` is ``context``'
        )

        class FailingTestMappingCopy2(TestMappingDelItem):
            def copy(self):
                return self.__class__()

        fmtester = FullMappingTester(
            FailingTestMappingCopy2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(KeyError, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '\'foo\''
        )

        class FailingTestMappingCopy3(TestMappingDelItem):
            def copy(self):
                new = self.__class__()
                new.update([('foo', object())])
                return new

        fmtester = FullMappingTester(
            FailingTestMappingCopy3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '``copied[\'foo\']`` is not ``context[\'foo\']``'
        )

        fmtester = FullMappingTester(
            TestMappingCopy,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_copy()

        class FailingTestNodeCopy(TestNodeSetItem, TestMappingCopy):
            pass

        fmtester = FullMappingTester(FailingTestNodeCopy)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '__name__ of copied does not match'
        )

        class FailingTestNodeCopy2(TestNodeSetItem, TestMappingCopy):
            def copy(self):
                new = self.__class__()
                new.__name__ = self.__name__
                new.update(self.items())
                return new

        fmtester = FullMappingTester(FailingTestNodeCopy2)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '__parent__ of copied does not match'
        )

        fmtester = FullMappingTester(TestNodeCopy)
        fmtester.test___setitem__()
        fmtester.test_copy()

    def test_setdefault(self):
        fmtester = FullMappingTester(TestNodeCopy)
        err = self.except_error(AttributeError, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            '\'TestNodeCopy\' object has no attribute \'setdefault\''
        )

        class FailingTestMappingSetDefault(TestMappingCopy):
            def setdefault(self, key, value=None):
                return value

        fmtester = FullMappingTester(
            FailingTestMappingSetDefault,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            'Replaced already existing item.'
        )

        class FailingTestMappingSetDefault2(TestMappingCopy):
            def setdefault(self, key, value=None):
                self[key] = object()
                return self[key]

        fmtester = FullMappingTester(
            FailingTestMappingSetDefault2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            'Inserted item not same instance.'
        )

        fmtester = FullMappingTester(
            TestMappingSetDefault,
            include_node_checks=False
        )
        fmtester.context['foo'] = TestMappingSetDefault()
        fmtester.context['baz'] = TestMappingSetDefault()
        fmtester.test_setdefault()

    def test_pop(self):
        fmtester = FullMappingTester(
            TestMappingSetDefault,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_pop)
        self.assertEqual(
            str(err),
            '\'TestMappingSetDefault\' object has no attribute \'pop\''
        )

        class FailingTestMappingPop(TestMappingSetDefault):
            def pop(self, key, default=None):
                return object()

        fmtester = FullMappingTester(
            FailingTestMappingPop,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Expected ``KeyError`` for inexistent item.'
        )

        class FailingTestMappingPop2(TestMappingSetDefault):
            def pop(self, key, default=None):
                if default is not None:
                    return object()
                raise KeyError

        fmtester = FullMappingTester(
            FailingTestMappingPop2,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Returned default is not same instance'
        )

        class FailingTestMappingPop3(TestMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return object()
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(
            FailingTestMappingPop3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Popped item not same instance'
        )

        class FailingTestMappingPop4(TestMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return self.data['foo']
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(
            FailingTestMappingPop4,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Invalid mapping length after ``pop``'
        )

        fmtester = FullMappingTester(
            TestMappingPop,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.context['baz'] = TestMappingSetDefault()
        fmtester.test_pop()

    def test_popitem(self):
        fmtester = FullMappingTester(
            TestMappingPop,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            '\'TestMappingPop\' object has no attribute \'popitem\''
        )

        class FailingTestMappingPopItem(TestMappingPop):
            def popitem(self):
                return

        fmtester = FullMappingTester(
            FailingTestMappingPopItem,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            'Expected 1-length result. Got ``2``'
        )

        class FailingTestMappingPopItem2(TestMappingPop):
            def popitem(self):
                try:
                    return self.data.popitem()
                except Exception:
                    pass

        fmtester = FullMappingTester(
            FailingTestMappingPopItem2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            'Expected ``KeyError`` when called on empty mapping'
        )

        fmtester = FullMappingTester(
            TestMappingPopItem,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_popitem()

    def test_clear(self):
        fmtester = FullMappingTester(
            TestMappingPopItem,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_clear)
        self.assertEqual(
            str(err),
            '\'TestMappingPopItem\' object has no attribute \'clear\''
        )

        class FailingTestMappingClear(TestMappingClear):
            def clear(self):
                pass

        fmtester = FullMappingTester(
            FailingTestMappingClear,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_clear)
        self.assertEqual(
            str(err),
            'Expected 0-length result. Got ``2``'
        )

        fmtester = FullMappingTester(
            TestMappingClear,
            include_node_checks=False
        )
        fmtester.test_clear()

    def test_mapping(self):
        fmtester = FullMappingTester(
            TestMappingAll,
            include_node_checks=False
        )
        fmtester.run()
        self.assertEqual(fmtester.combined.split('\n'), [
            '``__contains__``: OK',
            '``__delitem__``: OK',
            '``__getitem__``: OK',
            '``__iter__``: OK',
            '``__len__``: OK',
            '``__setitem__``: OK',
            '``clear``: OK',
            '``copy``: OK',
            '``get``: OK',
            '``has_key``: OK',
            '``items``: OK',
            '``iteritems``: OK',
            '``iterkeys``: OK',
            '``itervalues``: OK',
            '``keys``: OK',
            '``pop``: OK',
            '``popitem``: OK',
            '``setdefault``: OK',
            '``update``: OK',
            '``values``: OK'
        ])

    def test_node(self):
        fmtester = FullMappingTester(TestNodeAll)
        fmtester.run()
        self.assertEqual(fmtester.combined.split('\n'), [
            '``__contains__``: OK',
            '``__delitem__``: OK',
            '``__getitem__``: OK',
            '``__iter__``: OK',
            '``__len__``: OK',
            '``__setitem__``: OK',
            '``clear``: OK',
            '``copy``: OK',
            '``get``: OK',
            '``has_key``: OK',
            '``items``: OK',
            '``iteritems``: OK',
            '``iterkeys``: OK',
            '``itervalues``: OK',
            '``keys``: OK',
            '``pop``: OK',
            '``popitem``: OK',
            '``setdefault``: OK',
            '``update``: OK',
            '``values``: OK'
        ])


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover

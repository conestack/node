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

class MockMapping(object):
    def __init__(self):
        self.data = dict()


class MockMappingSetItem(MockMapping):
    def __setitem__(self, key, value):
        self.data[key] = value


class MockMappingGetItem(MockMappingSetItem):
    def __getitem__(self, key):
        return self.data[key]


class MockMappingGet(MockMappingGetItem):
    def get(self, key, default=None):
        return self.data.get(key, default)


class MockMappingIter(MockMappingGet):
    def __iter__(self):
        return self.data.__iter__()


class MockMappingKeys(MockMappingIter):
    def keys(self):
        return [k for k in self.data]


class MockMappingIterKeys(MockMappingKeys):
    def iterkeys(self):
        return self.data.__iter__()


class MockMappingValues(MockMappingIterKeys):
    def values(self):
        return self.data.values()


class MockMappingIterValues(MockMappingValues):
    def itervalues(self):
        return iter(self.data.values())


class MockMappingItems(MockMappingIterValues):
    def items(self):
        return self.data.items()


class MockMappingIterItems(MockMappingItems):
    def iteritems(self):
        return iter(self.data.items())


class MockMappingContains(MockMappingIterItems):
    def __contains__(self, key):
        return key in self.data


class MockMappingHasKey(MockMappingContains):
    def has_key(self, key):
        return self.data.has_key(key) if IS_PY2 else key in self.data


class MockMappingLen(MockMappingHasKey):
    def __len__(self):
        return len(self.data)


class MockMappingUpdate(MockMappingLen):
    def update(self, data=(), **kw):
        for key, value in data:
            self[key] = value
        for key, value in getattr(kw, ITER_FUNC)():
            self[key] = value


class MockMappingDelItem(MockMappingUpdate):
    def __delitem__(self, key):
        del self.data[key]


class MockMappingCopy(MockMappingDelItem):
    def copy(self):
        new = self.__class__()
        new.update(self.items())
        return new


class MockMappingSetDefault(MockMappingCopy):
    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value


class MockMappingPop(MockMappingSetDefault):
    def pop(self, key, default=None):
        if default is not None:
            return self.data.pop(key, default)
        return self.data.pop(key)


class MockMappingPopItem(MockMappingPop):
    def popitem(self):
        return self.data.popitem()


class MockMappingClear(MockMappingPopItem):
    def clear(self):
        self.data.clear()


class MockMappingAll(MockMappingClear):
    pass


class MockNode(MockMapping):
    def __init__(self, name=None, parent=None):
        super(MockNode, self).__init__()
        self.__name__ = name
        self.__parent__ = parent


class MockNodeSetItem(MockNode, MockMappingSetItem):
    def __setitem__(self, name, value):
        value.__parent__ = self
        value.__name__ = name
        self.data[name] = value


class MockNodeGetItem(MockNodeSetItem, MockMappingGetItem):
    pass


class MockNodeValues(MockNodeSetItem, MockMappingValues):
    pass


class MockNodeItems(MockNodeSetItem, MockMappingItems):
    pass


class MockNodeCopy(MockNodeSetItem, MockMappingCopy):
    def copy(self):
        new = self.__class__()
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        new.update(self.items())
        return new


class MockNodeAll(MockNodeCopy, MockMappingAll):
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
        fmtester = FullMappingTester(MockMapping)
        err = self.except_error(TypeError, fmtester.test___setitem__)
        self.assertEqual(
            str(err),
            '\'MockMapping\' object does not support item assignment'
        )

        class FailingMockMappingSetItem(MockMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        fmtester = FullMappingTester(FailingMockMappingSetItem)
        err = self.except_error(TypeError, fmtester.test___setitem__)
        self.assertEqual(
            str(err),
            '__init__() got an unexpected keyword argument \'name\''
        )

        fmtester = FullMappingTester(MockNodeSetItem)
        fmtester.test___setitem__()

    def test___getitem__(self):
        fmtester = FullMappingTester(MockMapping)
        expected = '\'MockMapping\' object has no attribute \'__getitem__\'' \
            if (IS_PY2 and not IS_PYPY) else \
            '\'MockMapping\' object is not subscriptable'
        err = self.except_error(TypeError, fmtester.test___getitem__)
        self.assertEqual(str(err), expected)

        fmtester = FullMappingTester(MockMappingGetItem)
        fmtester.context['foo'] = MockMappingGetItem()
        fmtester.context['bar'] = MockMappingGetItem()
        err = self.except_error(AttributeError, fmtester.test___getitem__)
        self.assertEqual(
            str(err),
            '\'MockMappingGetItem\' object has no attribute \'__name__\''
        )

        class FailingMockNodeSetItem(MockNode, MockMappingSetItem):
            pass

        class FailingMockNodeGetItem(FailingMockNodeSetItem,
                                     MockMappingGetItem):
            pass

        fmtester = FullMappingTester(FailingMockNodeGetItem)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___getitem__)
        self.assertEqual(
            str(err),
            'Child ``bar`` has wrong ``__name__``'
        )

        fmtester = FullMappingTester(MockNodeGetItem)
        fmtester.test___setitem__()
        fmtester.test___getitem__()

    def test_get(self):
        fmtester = FullMappingTester(MockNodeGetItem)
        err = self.except_error(AttributeError, fmtester.test_get)
        self.assertEqual(
            str(err),
            '\'MockNodeGetItem\' object has no attribute \'get\''
        )

        class FailingMockMappingGet(MockMappingGetItem):
            def get(self, key, default=None):
                return object()

        fmtester = FullMappingTester(
            FailingMockMappingGet,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_get)
        self.assertTrue(
            str(err).startswith('Expected default, got <object object at')
        )

        class FailingMockMappingGet2(MockMappingGetItem):
            def get(self, key, default=None):
                return default

        fmtester = FullMappingTester(
            FailingMockMappingGet2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_get)
        self.assertEqual(
            str(err),
            'Expected value, got default'
        )

        fmtester = FullMappingTester(
            MockMappingGet,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_get()

    def test___iter__(self):
        fmtester = FullMappingTester(MockMapping)
        err = self.except_error(TypeError, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            '\'MockMapping\' object is not iterable'
        )

        class FailingMockMappingIter(MockMappingGet):
            def __iter__(self):
                return iter(list())

        fmtester = FullMappingTester(FailingMockMappingIter)
        err = self.except_error(Exception, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class FailingMockMappingIter2(MockMappingGet):
            def __iter__(self):
                return iter(['a', 'b'])

        fmtester = FullMappingTester(FailingMockMappingIter2)
        err = self.except_error(Exception, fmtester.test___iter__)
        self.assertEqual(
            str(err),
            'Expected ``[\'a\', \'b\']`` as keys. Got ``[\'foo\', \'bar\']``'
        )

        fmtester = FullMappingTester(
            MockMappingIter,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___iter__()

    def test_keys(self):
        fmtester = FullMappingTester(
            MockMappingIter,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_keys)
        self.assertEqual(
            str(err),
            '\'MockMappingIter\' object has no attribute \'keys\''
        )

        fmtester = FullMappingTester(
            MockMappingKeys,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_keys()

    def test_iterkeys(self):
        fmtester = FullMappingTester(
            MockMappingKeys,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_iterkeys)
        self.assertEqual(
            str(err),
            '\'MockMappingKeys\' object has no attribute \'iterkeys\''
        )

        fmtester = FullMappingTester(
            MockMappingIterKeys,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_iterkeys()

    def test_values(self):
        fmtester = FullMappingTester(
            MockMappingIterKeys,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_values)
        self.assertEqual(
            str(err),
            '\'MockMappingIterKeys\' object has no attribute \'values\''
        )

        fmtester = FullMappingTester(
            MockMappingValues,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_values)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        fmtester.test___setitem__()
        fmtester.test_values()

        fmtester = FullMappingTester(MockMappingValues)
        fmtester.context['foo'] = MockMappingValues()
        fmtester.context['bar'] = MockMappingValues()

        err = self.except_error(AttributeError, fmtester.test_values)
        self.assertEqual(
            str(err),
            '\'MockMappingValues\' object has no attribute \'__name__\''
        )

        class FailingMockNodeValues(MockNode, MockMappingValues):
            pass

        fmtester = FullMappingTester(FailingMockNodeValues)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_values)
        self.assertEqual(
            str(err),
            'Expected __name__ of value invalid. Got ``None``'
        )

        fmtester = FullMappingTester(MockNodeValues)
        fmtester.test___setitem__()
        fmtester.test_values()

    def test_itervalues(self):
        fmtester = FullMappingTester(MockNodeValues)
        err = self.except_error(AttributeError, fmtester.test_itervalues)
        self.assertEqual(
            str(err),
            '\'MockNodeValues\' object has no attribute \'itervalues\''
        )

        fmtester = FullMappingTester(
            MockMappingIterValues,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_itervalues()

    def test_items(self):
        fmtester = FullMappingTester(
            MockMappingIterValues,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_items)
        self.assertEqual(
            str(err),
            '\'MockMappingIterValues\' object has no attribute \'items\''
        )

        class FailingMockMappingItems(MockMappingIterValues):
            def items(self):
                return list()

        fmtester = FullMappingTester(
            FailingMockMappingItems,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        class FailingMockMappingItems2(MockMappingIterValues):
            def items(self):
                return [('foo', object()), ('b', object())]

        fmtester = FullMappingTester(
            FailingMockMappingItems2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected keys ``[\'foo\', \'bar\']``. Got ``b``'
        )

        class FailingMockMappingItems3(MockMappingIterValues):
            def items(self):
                return [('foo', object()), ('bar', object())]

        fmtester = FullMappingTester(
            FailingMockMappingItems3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertTrue(str(err).find('Expected <object object at') > -1)
        self.assertTrue(str(err).find('got <node.', 26) > -1)
        self.assertTrue(str(err).find('FailingMockMappingItems3', 38) > -1)

        fmtester = FullMappingTester(
            MockMappingItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_items()

        class FailingMockNodeItems(MockNode, MockMappingItems):
            pass

        fmtester = FullMappingTester(FailingMockNodeItems)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_items)
        self.assertEqual(
            str(err),
            'Expected same value for ``key`` "foo" and ``__name__`` "None"'
        )

        fmtester = FullMappingTester(MockNodeItems)
        fmtester.test___setitem__()
        fmtester.test_items()

    def test_iteritems(self):
        fmtester = FullMappingTester(MockMappingItems)
        err = self.except_error(AttributeError, fmtester.test_iteritems)
        self.assertEqual(
            str(err),
            '\'MockMappingItems\' object has no attribute \'iteritems\''
        )

        fmtester = FullMappingTester(
            MockMappingIterItems,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_iteritems()

    def test___contains__(self):
        class FailingMockMappingContains(MockMappingIterItems):
            def __contains__(self, key):
                return False

        fmtester = FullMappingTester(
            FailingMockMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``__contains__``'
        )

        class FailingMockMappingContains2(MockMappingIterItems):
            def __contains__(self, key):
                return True

        fmtester = FullMappingTester(
            FailingMockMappingContains2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___contains__)
        self.assertEqual(
            str(err),
            'Expected __contains__ to return False for non-existent key'
        )

        fmtester = FullMappingTester(
            MockMappingContains,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___contains__()

    def test_has_key(self):
        fmtester = FullMappingTester(
            MockMappingContains,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            '\'MockMappingContains\' object has no attribute \'has_key\''
        )

        class FailingMockMappingHasKey(MockMappingContains):
            def has_key(self, key):
                return False

        fmtester = FullMappingTester(
            FailingMockMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_has_key)
        self.assertEqual(
            str(err),
            'Expected ``foo`` and ``bar`` return ``True`` by ``has_key``'
        )

        fmtester = FullMappingTester(
            MockMappingHasKey,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_has_key()

    def test___len__(self):
        fmtester = FullMappingTester(
            MockMappingHasKey,
            include_node_checks=False
        )
        expected = '\'MockMappingHasKey\' has no length' if IS_PYPY else \
            'object of type \'MockMappingHasKey\' has no len()'
        err = self.except_error(TypeError, fmtester.test___len__)
        self.assertEqual(str(err), expected)

        class FailingMockMappingLen(MockMappingHasKey):
            def __len__(self):
                return 0

        fmtester = FullMappingTester(
            FailingMockMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test___len__)
        self.assertEqual(
            str(err),
            'Expected 2-length result. Got ``0``'
        )

        fmtester = FullMappingTester(
            MockMappingLen,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test___len__()

    def test_update(self):
        fmtester = FullMappingTester(
            MockMappingLen,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_update)
        self.assertEqual(
            str(err),
            '\'MockMappingLen\' object has no attribute \'update\''
        )

        class FailingMockMappingUpdate(MockMappingLen):
            def update(self, data=(), **kw):
                pass

        fmtester = FullMappingTester(FailingMockMappingUpdate)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'KeyError, Expected ``baz`` and ``blub`` after update'
        )

        class FailingMockMappingUpdate2(MockMappingLen):
            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = object()
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = object()

        fmtester = FullMappingTester(FailingMockMappingUpdate2)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Object at ``baz`` not expected one after update'
        )

        class FailingMockMappingUpdate3(MockMappingLen):
            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = object()

        fmtester = FullMappingTester(FailingMockMappingUpdate3)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Object at ``blub`` not expected one after update'
        )

        class BrokenData(dict):
            def __delitem__(self, key):
                if key == 'blub':
                    raise Exception(u"Broken implementation")

        class FailingMockMappingUpdate4(MockMappingLen):
            def __init__(self):
                self.data = BrokenData()

            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = value

        fmtester = FullMappingTester(FailingMockMappingUpdate4)
        err = self.except_error(RuntimeError, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Cannot del test key.'
        )

        class FailingMockMappingUpdate5(MockMappingLen):
            def update(self, data=(), data1=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in getattr(kw, ITER_FUNC)():
                    self[key] = value

        fmtester = FullMappingTester(FailingMockMappingUpdate5)
        err = self.except_error(Exception, fmtester.test_update)
        self.assertEqual(
            str(err),
            'Expected TypeError for update with more than one positional '
            'argument.'
        )

        fmtester = FullMappingTester(MockMappingUpdate)
        fmtester.test_update()

    def test___delitem__(self):
        fmtester = FullMappingTester(MockMappingUpdate)
        expected = '__delitem__' if not IS_PYPY else \
            '\'MockMappingUpdate\' object does not support item deletion'
        exc = TypeError if IS_PYPY else AttributeError
        err = self.except_error(exc, fmtester.test___delitem__)
        self.assertEqual(str(err), expected)

        fmtester = FullMappingTester(
            MockMappingDelItem,
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
            MockMappingDelItem,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '\'MockMappingDelItem\' object has no attribute \'copy\''
        )

        class FailingMockMappingCopy(MockMappingDelItem):
            def copy(self):
                return self

        fmtester = FullMappingTester(
            FailingMockMappingCopy,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '``copied`` is ``context``'
        )

        class FailingMockMappingCopy2(MockMappingDelItem):
            def copy(self):
                return self.__class__()

        fmtester = FullMappingTester(
            FailingMockMappingCopy2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(KeyError, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '\'foo\''
        )

        class FailingMockMappingCopy3(MockMappingDelItem):
            def copy(self):
                new = self.__class__()
                new.update([('foo', object())])
                return new

        fmtester = FullMappingTester(
            FailingMockMappingCopy3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '``copied[\'foo\']`` is not ``context[\'foo\']``'
        )

        fmtester = FullMappingTester(
            MockMappingCopy,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_copy()

        class FailingMockNodeCopy(MockNodeSetItem, MockMappingCopy):
            pass

        fmtester = FullMappingTester(FailingMockNodeCopy)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '__name__ of copied does not match'
        )

        class FailingMockNodeCopy2(MockNodeSetItem, MockMappingCopy):
            def copy(self):
                new = self.__class__()
                new.__name__ = self.__name__
                new.update(self.items())
                return new

        fmtester = FullMappingTester(FailingMockNodeCopy2)
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_copy)
        self.assertEqual(
            str(err),
            '__parent__ of copied does not match'
        )

        fmtester = FullMappingTester(MockNodeCopy)
        fmtester.test___setitem__()
        fmtester.test_copy()

    def test_setdefault(self):
        fmtester = FullMappingTester(MockNodeCopy)
        err = self.except_error(AttributeError, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            '\'MockNodeCopy\' object has no attribute \'setdefault\''
        )

        class FailingMockMappingSetDefault(MockMappingCopy):
            def setdefault(self, key, value=None):
                return value

        fmtester = FullMappingTester(
            FailingMockMappingSetDefault,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            'Replaced already existing item.'
        )

        class FailingMockMappingSetDefault2(MockMappingCopy):
            def setdefault(self, key, value=None):
                self[key] = object()
                return self[key]

        fmtester = FullMappingTester(
            FailingMockMappingSetDefault2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_setdefault)
        self.assertEqual(
            str(err),
            'Inserted item not same instance.'
        )

        fmtester = FullMappingTester(
            MockMappingSetDefault,
            include_node_checks=False
        )
        fmtester.context['foo'] = MockMappingSetDefault()
        fmtester.context['baz'] = MockMappingSetDefault()
        fmtester.test_setdefault()

    def test_pop(self):
        fmtester = FullMappingTester(
            MockMappingSetDefault,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_pop)
        self.assertEqual(
            str(err),
            '\'MockMappingSetDefault\' object has no attribute \'pop\''
        )

        class FailingMockMappingPop(MockMappingSetDefault):
            def pop(self, key, default=None):
                return object()

        fmtester = FullMappingTester(
            FailingMockMappingPop,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Expected ``KeyError`` for inexistent item.'
        )

        class FailingMockMappingPop2(MockMappingSetDefault):
            def pop(self, key, default=None):
                if default is not None:
                    return object()
                raise KeyError

        fmtester = FullMappingTester(
            FailingMockMappingPop2,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Returned default is not same instance'
        )

        class FailingMockMappingPop3(MockMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return object()
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(
            FailingMockMappingPop3,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Popped item not same instance'
        )

        class FailingMockMappingPop4(MockMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return self.data['foo']
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(
            FailingMockMappingPop4,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_pop)
        self.assertEqual(
            str(err),
            'Invalid mapping length after ``pop``'
        )

        fmtester = FullMappingTester(
            MockMappingPop,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.context['baz'] = MockMappingSetDefault()
        fmtester.test_pop()

    def test_popitem(self):
        fmtester = FullMappingTester(
            MockMappingPop,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            '\'MockMappingPop\' object has no attribute \'popitem\''
        )

        class FailingMockMappingPopItem(MockMappingPop):
            def popitem(self):
                return

        fmtester = FullMappingTester(
            FailingMockMappingPopItem,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            'Expected 1-length result. Got ``2``'
        )

        class FailingMockMappingPopItem2(MockMappingPop):
            def popitem(self):
                try:
                    return self.data.popitem()
                except Exception:
                    pass

        fmtester = FullMappingTester(
            FailingMockMappingPopItem2,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        err = self.except_error(Exception, fmtester.test_popitem)
        self.assertEqual(
            str(err),
            'Expected ``KeyError`` when called on empty mapping'
        )

        fmtester = FullMappingTester(
            MockMappingPopItem,
            include_node_checks=False
        )
        fmtester.test___setitem__()
        fmtester.test_popitem()

    def test_clear(self):
        fmtester = FullMappingTester(
            MockMappingPopItem,
            include_node_checks=False
        )
        err = self.except_error(AttributeError, fmtester.test_clear)
        self.assertEqual(
            str(err),
            '\'MockMappingPopItem\' object has no attribute \'clear\''
        )

        class FailingMockMappingClear(MockMappingClear):
            def clear(self):
                pass

        fmtester = FullMappingTester(
            FailingMockMappingClear,
            include_node_checks=False
        )
        err = self.except_error(Exception, fmtester.test_clear)
        self.assertEqual(
            str(err),
            'Expected 0-length result. Got ``2``'
        )

        fmtester = FullMappingTester(
            MockMappingClear,
            include_node_checks=False
        )
        fmtester.test_clear()

    def test_mapping(self):
        fmtester = FullMappingTester(
            MockMappingAll,
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
        fmtester = FullMappingTester(MockNodeAll)
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

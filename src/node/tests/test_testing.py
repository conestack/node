from node.compat import IS_PY2
from node.compat import IS_PYPY
from node.compat import iteritems
from node.testing import FullMappingTester
from node.testing.base import BaseTester
from node.testing.base import ContractError
from node.testing.base import create_tree
from node.testing.env import MyNode
from node.tests import NodeTestCase
from node.tests import unittest
from odict import odict


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
        for key, value in iteritems(kw):
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

class TestEnv(unittest.TestCase):

    def test_MyNode(self):
        # test IFullMapping contract on MyNode
        mynode = MyNode()
        self.assertIsInstance(mynode, MyNode)
        # __setitem__
        foo = mynode['foo'] = MyNode()
        bar = mynode['bar'] = MyNode(name='xxx')
        # __getitem__
        self.assertEqual(mynode['foo'], foo)
        self.assertEqual(mynode['bar'].__name__, 'bar')
        # get
        self.assertEqual(mynode.get('bar'), bar)
        self.assertEqual(mynode.get('xxx', 'default'), 'default')
        # __iter__
        self.assertEqual([key for key in mynode], ['foo', 'bar'])
        # keys
        self.assertEqual(mynode.keys(), ['foo', 'bar'])
        # iterkeys
        self.assertEqual([key for key in mynode.iterkeys()], ['foo', 'bar'])
        # values
        self.assertEqual(mynode.values(), [foo, bar])
        # itervalues
        self.assertEqual([val for val in mynode.itervalues()], [foo, bar])
        # items
        self.assertEqual(mynode.items(), [
            ('foo', foo),
            ('bar', bar)
        ])
        # iteritems
        self.assertEqual([item for item in mynode.iteritems()], [
            ('foo', foo),
            ('bar', bar)
        ])
        # __contains__
        self.assertTrue('bar' in mynode)
        # has_key
        self.assertTrue(mynode.has_key('foo'))
        # __len__
        self.assertEqual(len(mynode), 2)
        # update
        baz = MyNode()
        mynode.update((('baz', baz),))
        self.assertEqual(mynode['baz'], baz)
        # __delitem__
        del mynode['bar']
        self.assertEqual(mynode.keys(), ['foo', 'baz'])
        # copy
        mycopied = mynode.copy()
        self.assertTrue(str(mycopied).find('<MyNode object \'None\' at ') > -1)
        self.assertFalse(mycopied is mynode)
        self.assertTrue(mycopied['foo'] is foo)
        self.assertTrue(mycopied['baz'] is baz)
        self.assertEqual(mycopied.items(), [
            ('foo', foo),
            ('baz', baz)
        ])
        # setdefault
        mynew = MyNode()
        self.assertFalse(mynode.setdefault('foo', mynew) is mynew)
        self.assertTrue(mynode.setdefault('bar', mynew) is mynew)
        self.assertEqual(mynode.items(), [
            ('foo', foo),
            ('baz', baz),
            ('bar', mynew)
        ])
        # pop
        self.assertRaises(KeyError, mynode.pop, 'xxx')
        self.assertEqual(mynode.pop('xxx', 'default'), 'default')
        self.assertEqual(mynode.pop('foo'), foo)
        self.assertEqual(mynode.keys(), ['baz', 'bar'])
        # popitem and clear
        self.assertEqual(mynode.popitem(), ('bar', mynew))
        self.assertEqual(mynode.keys(), ['baz'])
        mynode.clear()
        self.assertEqual(mynode.keys(), [])
        self.assertRaises(KeyError, mynode.popitem)


class TestBase(NodeTestCase):

    def test_create_tree(self):
        self.assertEqual(create_tree(odict), odict([
            ('child_0', odict([
                ('subchild_0', odict()),
                ('subchild_1', odict())
            ])),
            ('child_1', odict([
                ('subchild_0', odict()),
                ('subchild_1', odict())
            ])),
            ('child_2', odict([
                ('subchild_0', odict()),
                ('subchild_1', odict())
            ]))
        ]))

    def test_BaseTester(self):
        # BaseTester is used to write testing code for an interface contract.
        # A subclass must define ``iface_contract`` containing the functions
        # names of interface to be tested and a testing function for each
        # contract function prefixed with 'test_'
        class DummyTester(BaseTester):
            iface_contract = ['func_a', 'func_b', 'func_c']

            def test_func_a(self):
                self.context.func_a()

            def test_func_b(self):
                self.context.func_b()

            def test_func_c(self):
                self.context.func_c()

        # Test implementations
        class FuncAImpl(object):

            def func_a(self):
                pass

        class FuncBImpl(FuncAImpl):

            def func_b(self):
                raise Exception('func_b failed')

        # Tester object expects the implementation class on init, and optional
        # a already instantiated testing instance. If context is not given,
        # it is instantiated by given class without arguments
        tester = DummyTester(FuncBImpl)

        # Run and print combined results
        tester.run()
        self.checkOutput("""
        ``func_a``: OK
        ``func_b``: failed: Exception('func_b failed'...)
        ``func_c``: failed: AttributeError("'FuncBImpl' object has no attribute 'func_c'"...)
        """, tester.combined)

        # Get results of testing as odict
        self.assertEqual(
            sorted(tester.results.keys()),
            ['func_a', 'func_b', 'func_c']
        )
        self.assertEqual(tester.results['func_a'], 'OK')
        self.assertTrue(tester.results['func_b'].find('Exception(\'func_b failed') > -1)
        self.assertTrue(tester.results['func_c'].find('AttributeError("\'FuncBImpl\'') > -1)

        # Print classes which actually provides the function implementation
        self.assertEqual(tester.wherefrom.split('\n'), [
            'func_a: FuncAImpl',
            'func_b: FuncBImpl',
            'func_c: function not found on object'
        ])

        # A tester can be forced to raise exceptions directly instead of
        # collecting them
        tester.direct_error = True
        err = None
        try:
            tester.run()
        except Exception as e:
            err = e
        finally:
            self.assertEqual(str(err), 'func_b failed')

        # If tester does define a function to test in ``iface_contract`` but
        # not implements the related testing function, ``run`` will fail
        class BrokenTester(BaseTester):
            iface_contract = ['test_me']

        err = None
        try:
            tester = BrokenTester(FuncBImpl)
            tester.run()
        except ContractError as e:
            err = e
        finally:
            self.assertEqual(
                str(err),
                '``BrokenTester`` does not provide ``test_test_me``'
            )


class TestFullmapping(NodeTestCase):

    def test___setitem__(self):
        fmtester = FullMappingTester(MockMapping)
        err = self.expectError(TypeError, fmtester.test___setitem__)
        exp = '\'MockMapping\' object does not support item assignment'
        self.assertEqual(str(err), exp)

        class FailingMockMappingSetItem(MockMapping):
            def __setitem__(self, key, value):
                self.data[key] = value

        fmtester = FullMappingTester(FailingMockMappingSetItem)
        err = self.expectError(TypeError, fmtester.test___setitem__)
        exp = '__init__() got an unexpected keyword argument \'name\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockNodeSetItem)
        fmtester.test___setitem__()

    def test___getitem__(self):
        fmtester = FullMappingTester(MockMapping)
        err = self.expectError(TypeError, fmtester.test___getitem__)
        exp = '\'MockMapping\' object has no attribute \'__getitem__\'' \
            if (IS_PY2 and not IS_PYPY) else \
            '\'MockMapping\' object is not subscriptable'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingGetItem)
        fmtester.context['foo'] = MockMappingGetItem()
        fmtester.context['bar'] = MockMappingGetItem()
        err = self.expectError(AttributeError, fmtester.test___getitem__)
        exp = '\'MockMappingGetItem\' object has no attribute \'__name__\''
        self.assertEqual(str(err), exp)

        class FailingMockNodeSetItem(MockNode, MockMappingSetItem):
            pass

        class FailingMockNodeGetItem(FailingMockNodeSetItem,
                                     MockMappingGetItem):
            pass

        fmtester = FullMappingTester(FailingMockNodeGetItem)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test___getitem__)
        self.assertEqual(str(err), 'Child ``bar`` has wrong ``__name__``')

        fmtester = FullMappingTester(MockNodeGetItem)
        fmtester.test___setitem__()
        fmtester.test___getitem__()

    def test_get(self):
        fmtester = FullMappingTester(MockNodeGetItem)
        err = self.expectError(AttributeError, fmtester.test_get)
        exp = '\'MockNodeGetItem\' object has no attribute \'get\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingGet(MockMappingGetItem):
            def get(self, key, default=None):
                return object()

        fmtester = FullMappingTester(FailingMockMappingGet, node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_get)
        exp = 'Expected default, got <object object at'
        self.assertTrue(str(err).startswith(exp))

        class FailingMockMappingGet2(MockMappingGetItem):
            def get(self, key, default=None):
                return default

        fmtester = FullMappingTester(FailingMockMappingGet2, node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_get)
        self.assertEqual(str(err), 'Expected value, got default')

        fmtester = FullMappingTester(MockMappingGet, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_get()

    def test___iter__(self):
        fmtester = FullMappingTester(MockMapping)
        err = self.expectError(TypeError, fmtester.test___iter__)
        self.assertEqual(str(err), '\'MockMapping\' object is not iterable')

        class FailingMockMappingIter(MockMappingGet):
            def __iter__(self):
                return iter(list())

        fmtester = FullMappingTester(FailingMockMappingIter)
        err = self.expectError(Exception, fmtester.test___iter__)
        self.assertEqual(str(err), 'Expected 2-length result. Got ``0``')

        class FailingMockMappingIter2(MockMappingGet):
            def __iter__(self):
                return iter(['a', 'b'])

        fmtester = FullMappingTester(FailingMockMappingIter2)
        err = self.expectError(Exception, fmtester.test___iter__)
        exp = 'Expected ``[\'a\', \'b\']`` as keys. Got ``[\'foo\', \'bar\']``'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingIter, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test___iter__()

    def test_keys(self):
        fmtester = FullMappingTester(MockMappingIter, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_keys)
        exp = '\'MockMappingIter\' object has no attribute \'keys\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingKeys, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_keys()

    def test_iterkeys(self):
        fmtester = FullMappingTester(MockMappingKeys, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_iterkeys)
        exp = '\'MockMappingKeys\' object has no attribute \'iterkeys\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingIterKeys, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_iterkeys()

    def test_values(self):
        fmtester = FullMappingTester(MockMappingIterKeys, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_values)
        exp = '\'MockMappingIterKeys\' object has no attribute \'values\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingValues, node_checks=False)
        err = self.expectError(Exception, fmtester.test_values)
        self.assertEqual(str(err), 'Expected 2-length result. Got ``0``')

        fmtester.test___setitem__()
        fmtester.test_values()

        fmtester = FullMappingTester(MockMappingValues)
        fmtester.context['foo'] = MockMappingValues()
        fmtester.context['bar'] = MockMappingValues()

        err = self.expectError(AttributeError, fmtester.test_values)
        exp = '\'MockMappingValues\' object has no attribute \'__name__\''
        self.assertEqual(str(err), exp)

        class FailingMockNodeValues(MockNode, MockMappingValues):
            pass

        fmtester = FullMappingTester(FailingMockNodeValues)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_values)
        exp = 'Expected __name__ of value invalid. Got ``None``'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockNodeValues)
        fmtester.test___setitem__()
        fmtester.test_values()

    def test_itervalues(self):
        fmtester = FullMappingTester(MockNodeValues)
        err = self.expectError(AttributeError, fmtester.test_itervalues)
        exp = '\'MockNodeValues\' object has no attribute \'itervalues\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingIterValues, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_itervalues()

    def test_items(self):
        fmtester = FullMappingTester(MockMappingIterValues, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_items)
        exp = '\'MockMappingIterValues\' object has no attribute \'items\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingItems(MockMappingIterValues):
            def items(self):
                return list()

        fmtester = FullMappingTester(FailingMockMappingItems,
                                     node_checks=False)
        err = self.expectError(Exception, fmtester.test_items)
        self.assertEqual(str(err), 'Expected 2-length result. Got ``0``')

        class FailingMockMappingItems2(MockMappingIterValues):
            def items(self):
                return [('foo', object()), ('b', object())]

        fmtester = FullMappingTester(FailingMockMappingItems2,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_items)
        exp = 'Expected keys ``[\'foo\', \'bar\']``. Got ``b``'
        self.assertEqual(str(err), exp)

        class FailingMockMappingItems3(MockMappingIterValues):
            def items(self):
                return [('foo', object()), ('bar', object())]

        fmtester = FullMappingTester(FailingMockMappingItems3,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_items)
        self.assertTrue(str(err).find('Expected <object object at') > -1)
        self.assertTrue(str(err).find('got <node.', 26) > -1)
        self.assertTrue(str(err).find('FailingMockMappingItems3', 38) > -1)

        fmtester = FullMappingTester(MockMappingItems, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_items()

        class FailingMockNodeItems(MockNode, MockMappingItems):
            pass

        fmtester = FullMappingTester(FailingMockNodeItems)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_items)
        exp = 'Expected same value for ``key`` "foo" and ``__name__`` "None"'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockNodeItems)
        fmtester.test___setitem__()
        fmtester.test_items()

    def test_iteritems(self):
        fmtester = FullMappingTester(MockMappingItems)
        err = self.expectError(AttributeError, fmtester.test_iteritems)
        exp = '\'MockMappingItems\' object has no attribute \'iteritems\''
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingIterItems, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_iteritems()

    def test___contains__(self):
        class FailingMockMappingContains(MockMappingIterItems):
            def __contains__(self, key):
                return False

        fmtester = FullMappingTester(FailingMockMappingContains,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test___contains__)
        exp = 'Expected ``foo`` and ``bar`` return ``True`` by ' \
              '``__contains__``'
        self.assertEqual(str(err), exp)

        class FailingMockMappingContains2(MockMappingIterItems):
            def __contains__(self, key):
                return True

        fmtester = FullMappingTester(FailingMockMappingContains2,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test___contains__)
        exp = 'Expected __contains__ to return False for non-existent key'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingContains, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test___contains__()

    def test_has_key(self):
        fmtester = FullMappingTester(MockMappingContains, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_has_key)
        exp = '\'MockMappingContains\' object has no attribute \'has_key\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingHasKey(MockMappingContains):
            def has_key(self, key):
                return False

        fmtester = FullMappingTester(FailingMockMappingHasKey,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_has_key)
        exp = 'Expected ``foo`` and ``bar`` return ``True`` by ``has_key``'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingHasKey, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_has_key()

    def test___len__(self):
        fmtester = FullMappingTester(MockMappingHasKey, node_checks=False)
        err = self.expectError(TypeError, fmtester.test___len__)
        exp = '\'MockMappingHasKey\' has no length' if IS_PYPY else \
            'object of type \'MockMappingHasKey\' has no len()'
        self.assertEqual(str(err), exp)

        class FailingMockMappingLen(MockMappingHasKey):
            def __len__(self):
                return 0

        fmtester = FullMappingTester(FailingMockMappingLen, node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test___len__)
        self.assertEqual(str(err), 'Expected 2-length result. Got ``0``')

        fmtester = FullMappingTester(MockMappingLen, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test___len__()

    def test_update(self):
        fmtester = FullMappingTester(MockMappingLen, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_update)
        exp = '\'MockMappingLen\' object has no attribute \'update\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingUpdate(MockMappingLen):
            def update(self, data=(), **kw):
                pass

        fmtester = FullMappingTester(FailingMockMappingUpdate)
        err = self.expectError(Exception, fmtester.test_update)
        exp = 'KeyError, Expected ``baz`` and ``blub`` after update'
        self.assertEqual(str(err), exp)

        class FailingMockMappingUpdate2(MockMappingLen):
            def update(self, data=(), **kw):
                for key, _ in data:
                    self[key] = object()
                for key, _ in iteritems(kw):
                    self[key] = object()

        fmtester = FullMappingTester(FailingMockMappingUpdate2)
        err = self.expectError(Exception, fmtester.test_update)
        exp = 'Object at ``baz`` not expected one after update'
        self.assertEqual(str(err), exp)

        class FailingMockMappingUpdate3(MockMappingLen):
            def update(self, data=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in iteritems(kw):
                    self[key] = object()

        fmtester = FullMappingTester(FailingMockMappingUpdate3)
        err = self.expectError(Exception, fmtester.test_update)
        exp = 'Object at ``blub`` not expected one after update'
        self.assertEqual(str(err), exp)

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
                for key, value in iteritems(kw):
                    self[key] = value

        fmtester = FullMappingTester(FailingMockMappingUpdate4)
        err = self.expectError(RuntimeError, fmtester.test_update)
        self.assertEqual(str(err), 'Cannot del test key.')

        class FailingMockMappingUpdate5(MockMappingLen):
            def update(self, data=(), data1=(), **kw):
                for key, value in data:
                    self[key] = value
                for key, value in iteritems(kw):
                    self[key] = value

        fmtester = FullMappingTester(FailingMockMappingUpdate5)
        err = self.expectError(Exception, fmtester.test_update)
        exp = 'Expected TypeError for update with more than one positional ' \
              'argument.'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingUpdate)
        fmtester.test_update()

    def test___delitem__(self):
        fmtester = FullMappingTester(MockMappingUpdate)
        exp = '__delitem__' if not IS_PYPY else \
            '\'MockMappingUpdate\' object does not support item deletion'
        exc = TypeError if IS_PYPY else AttributeError
        err = self.expectError(exc, fmtester.test___delitem__)
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingDelItem, node_checks=False)
        err = self.expectError(Exception, fmtester.test___delitem__)
        self.assertEqual(str(err), 'KeyError, expected ``bar``')

        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test___delitem__)
        self.assertEqual(str(err), 'Expected 2-length result. Got ``1``')

        fmtester.test___setitem__()
        fmtester.test_update()
        fmtester.test___delitem__()

    def test_copy(self):
        fmtester = FullMappingTester(MockMappingDelItem, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_copy)
        exp = '\'MockMappingDelItem\' object has no attribute \'copy\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingCopy(MockMappingDelItem):
            def copy(self):
                return self

        fmtester = FullMappingTester(FailingMockMappingCopy, node_checks=False)
        err = self.expectError(Exception, fmtester.test_copy)
        self.assertEqual(str(err), '``copied`` is ``context``')

        class FailingMockMappingCopy2(MockMappingDelItem):
            def copy(self):
                return self.__class__()

        fmtester = FullMappingTester(FailingMockMappingCopy2,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(KeyError, fmtester.test_copy)
        self.assertEqual(str(err), '\'foo\'')

        class FailingMockMappingCopy3(MockMappingDelItem):
            def copy(self):
                new = self.__class__()
                new.update([('foo', object())])
                return new

        fmtester = FullMappingTester(FailingMockMappingCopy3,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_copy)
        exp = '``copied[\'foo\']`` is not ``context[\'foo\']``'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingCopy, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_copy()

        class FailingMockNodeCopy(MockNodeSetItem, MockMappingCopy):
            pass

        fmtester = FullMappingTester(FailingMockNodeCopy)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_copy)
        self.assertEqual(str(err), '__name__ of copied does not match')

        class FailingMockNodeCopy2(MockNodeSetItem, MockMappingCopy):
            def copy(self):
                new = self.__class__()
                new.__name__ = self.__name__
                new.update(self.items())
                return new

        fmtester = FullMappingTester(FailingMockNodeCopy2)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_copy)
        self.assertEqual(str(err), '__parent__ of copied does not match')

        fmtester = FullMappingTester(MockNodeCopy)
        fmtester.test___setitem__()
        fmtester.test_copy()

    def test_setdefault(self):
        fmtester = FullMappingTester(MockNodeCopy)
        err = self.expectError(AttributeError, fmtester.test_setdefault)
        exp = '\'MockNodeCopy\' object has no attribute \'setdefault\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingSetDefault(MockMappingCopy):
            def setdefault(self, key, value=None):
                return value

        fmtester = FullMappingTester(FailingMockMappingSetDefault,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_setdefault)
        self.assertEqual(str(err), 'Replaced already existing item.')

        class FailingMockMappingSetDefault2(MockMappingCopy):
            def setdefault(self, key, value=None):
                self[key] = object()
                return self[key]

        fmtester = FullMappingTester(FailingMockMappingSetDefault2,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_setdefault)
        self.assertEqual(str(err), 'Inserted item not same instance.')

        fmtester = FullMappingTester(MockMappingSetDefault, node_checks=False)
        fmtester.context['foo'] = MockMappingSetDefault()
        fmtester.context['baz'] = MockMappingSetDefault()
        fmtester.test_setdefault()

    def test_pop(self):
        fmtester = FullMappingTester(MockMappingSetDefault, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_pop)
        exp = '\'MockMappingSetDefault\' object has no attribute \'pop\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingPop(MockMappingSetDefault):
            def pop(self, key, default=None):
                return object()

        fmtester = FullMappingTester(FailingMockMappingPop, node_checks=False)
        err = self.expectError(Exception, fmtester.test_pop)
        exp = 'Expected ``KeyError`` for inexistent item.'
        self.assertEqual(str(err), exp)

        class FailingMockMappingPop2(MockMappingSetDefault):
            def pop(self, key, default=None):
                if default is not None:
                    return object()
                raise KeyError

        fmtester = FullMappingTester(FailingMockMappingPop2, node_checks=False)
        err = self.expectError(Exception, fmtester.test_pop)
        self.assertEqual(str(err), 'Returned default is not same instance')

        class FailingMockMappingPop3(MockMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return object()
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(FailingMockMappingPop3, node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_pop)
        self.assertEqual(str(err), 'Popped item not same instance')

        class FailingMockMappingPop4(MockMappingSetDefault):
            def pop(self, key, default=None):
                if key == 'foo':
                    return self.data['foo']
                if default is not None:
                    return default
                raise KeyError

        fmtester = FullMappingTester(FailingMockMappingPop4, node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_pop)
        self.assertEqual(str(err), 'Invalid mapping length after ``pop``')

        fmtester = FullMappingTester(MockMappingPop, node_checks=False)
        fmtester.test___setitem__()
        fmtester.context['baz'] = MockMappingSetDefault()
        fmtester.test_pop()

    def test_popitem(self):
        fmtester = FullMappingTester(MockMappingPop, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_popitem)
        exp = '\'MockMappingPop\' object has no attribute \'popitem\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingPopItem(MockMappingPop):
            def popitem(self):
                return

        fmtester = FullMappingTester(FailingMockMappingPopItem,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_popitem)
        self.assertEqual(str(err), 'Expected 1-length result. Got ``2``')

        class FailingMockMappingPopItem2(MockMappingPop):
            def popitem(self):
                try:
                    return self.data.popitem()
                except Exception:
                    pass

        fmtester = FullMappingTester(FailingMockMappingPopItem2,
                                     node_checks=False)
        fmtester.test___setitem__()
        err = self.expectError(Exception, fmtester.test_popitem)
        exp = 'Expected ``KeyError`` when called on empty mapping'
        self.assertEqual(str(err), exp)

        fmtester = FullMappingTester(MockMappingPopItem, node_checks=False)
        fmtester.test___setitem__()
        fmtester.test_popitem()

    def test_clear(self):
        fmtester = FullMappingTester(MockMappingPopItem, node_checks=False)
        err = self.expectError(AttributeError, fmtester.test_clear)
        exp = '\'MockMappingPopItem\' object has no attribute \'clear\''
        self.assertEqual(str(err), exp)

        class FailingMockMappingClear(MockMappingClear):
            def clear(self):
                pass

        fmtester = FullMappingTester(FailingMockMappingClear,
                                     node_checks=False)
        err = self.expectError(Exception, fmtester.test_clear)
        self.assertEqual(str(err), 'Expected 0-length result. Got ``2``')

        fmtester = FullMappingTester(MockMappingClear, node_checks=False)
        fmtester.test_clear()

    def test_mapping(self):
        fmtester = FullMappingTester(MockMappingAll, node_checks=False)
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

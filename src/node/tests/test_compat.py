from node import compat
from node.tests import NodeTestCase
import functools
import warnings


class TestCompat(NodeTestCase):
    def deprecated_value(self, name):
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter('always')
            value = getattr(compat, name)
        self.assertEqual(len(log), 1)
        self.assertTrue(issubclass(log[0].category, DeprecationWarning))
        self.assertTrue(str(log[0].message).startswith(f'{name}: '))
        return value

    def test_IS_PYPY(self):
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter('always')
            self.assertIsInstance(compat.IS_PYPY, bool)
        self.assertEqual(log, [])

    def test_constants(self):
        self.assertFalse(self.deprecated_value('IS_PY2'))
        self.assertIs(self.deprecated_value('STR_TYPE'), str)
        self.assertIs(self.deprecated_value('UNICODE_TYPE'), str)
        self.assertEqual(self.deprecated_value('ITER_FUNC'), 'items')
        self.assertIs(self.deprecated_value('lru_cache'), functools.lru_cache)

    def test_iteritems(self):
        iteritems = self.deprecated_value('iteritems')
        self.assertEqual(list(iteritems({'a': 1})), [('a', 1)])

    def test_func_name(self):
        func_name = self.deprecated_value('func_name')
        self.assertEqual(func_name(len), 'len')

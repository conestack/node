from node.base import BaseNode
from node.behaviors import Adopt
from node.behaviors import Cache
from node.behaviors import ChildFactory
from node.behaviors import DefaultInit
from node.behaviors import Invalidate
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors import VolatileStorageInvalidate
from node.interfaces import ICache
from node.interfaces import IInvalidate
from node.tests import NodeTestCase
from plumber import plumbing


class TestCache(NodeTestCase):

    def test_Invalidate(self):
        # When using default ``Invalidate``, Contents of node just gets
        # deleted. Be aware this implementation must not be used on persisting
        # nodes.

        # Build invalidating node
        @plumbing(
            Adopt,
            Invalidate,
            DefaultInit,
            Nodify,
            OdictStorage)
        class Node(object):
            pass

        # Test tree
        root = Node()
        root['c1'] = Node()
        root['c2'] = Node()
        root['c2']['d1'] = Node()
        root['c2']['d2'] = Node()

        self.assertTrue(IInvalidate.providedBy(root))
        self.assertFalse(ICache.providedBy(root))

        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c1\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
            '    <class \'node.tests.test_cache.Node\'>: d1\n'
            '    <class \'node.tests.test_cache.Node\'>: d2\n'
        ))

        # Active invalidation of child by key
        root.invalidate(key='c1')
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
            '    <class \'node.tests.test_cache.Node\'>: d1\n'
            '    <class \'node.tests.test_cache.Node\'>: d2\n'
        ))

        err = self.expect_error(KeyError, root.invalidate, key='c1')
        self.assertEqual(str(err), '\'c1\'')

        # Active invalidation of all children
        root['c2'].invalidate()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
        ))

    def test_VolatileStorageInvalidate(self):
        # When a node internally uses a volatile storage like ``DictStorage``
        # or ``OdictStorage``, some can use ``VolatileStorageInvalidate`` for
        # invalidation
        @plumbing(
            Adopt,
            VolatileStorageInvalidate,
            DefaultInit,
            Nodify,
            OdictStorage)
        class Node(object):
            pass

        # Test tree:
        root = Node()
        root['c1'] = Node()
        root['c2'] = Node()
        root['c2']['d1'] = Node()
        root['c2']['d2'] = Node()

        self.assertTrue(IInvalidate.providedBy(root))
        self.assertFalse(ICache.providedBy(root))

        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c1\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
            '    <class \'node.tests.test_cache.Node\'>: d1\n'
            '    <class \'node.tests.test_cache.Node\'>: d2\n'
        ))

        # Active invalidation of child by key
        root.invalidate(key='c1')
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
            '    <class \'node.tests.test_cache.Node\'>: d1\n'
            '    <class \'node.tests.test_cache.Node\'>: d2\n'
        ))

        err = self.expect_error(KeyError, root.invalidate, key='c1')
        self.assertEqual(str(err), '\'c1\'')

        # Active invalidation of all children
        root['c2'].invalidate()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: c2\n'
        ))

    def test_with_ChildFactory(self):
        # Check for ChildFactory Node
        @plumbing(
            Adopt,
            VolatileStorageInvalidate,
            DefaultInit,
            Nodify,
            ChildFactory,
            OdictStorage)
        class Node(object):
            factories = {
                'foo': BaseNode,
                'bar': BaseNode,
            }

        node = Node()
        self.check_output("""\
        [('bar', <BaseNode object 'bar' at ...>),
        ('foo', <BaseNode object 'foo' at ...>)]
        """, str(sorted(node.items())))

        node.invalidate('foo')
        self.assertEqual(sorted(node.keys()), ['bar', 'foo'])

        self.check_output("""\
        [('bar', <BaseNode object 'bar' at ...>)]
        """, str(node.storage.items()))

        node.invalidate('foo')
        self.check_output("""\
        [('bar', <BaseNode object 'bar' at ...>)]
        """, str(node.storage.items()))

        node.invalidate()
        self.assertEqual(node.storage.items(), [])

        err = self.expect_error(KeyError, node.invalidate, 'baz')
        self.assertEqual(str(err), '\'baz\'')

    def test_Cache(self):
        # Build a node with active invalidation and cache functionality
        @plumbing(
            Adopt,
            Cache,
            Invalidate,
            DefaultInit,
            Nodify,
            OdictStorage)
        class Node(object):
            pass

        root = Node()
        root['c1'] = Node()
        root['c2'] = Node()
        root['c2']['d1'] = Node()
        root['c2']['d2'] = Node()

        self.assertTrue(IInvalidate.providedBy(root))
        self.assertTrue(ICache.providedBy(root))

        # We just accessed 'c2' above, only cached value on root at the moment
        self.assertEqual(list(root.cache.keys()), ['c2'])
        expected = '<Node object \'c2\' at'
        self.assertTrue(str(root.cache['c2']).startswith(expected))

        expected = '<Node object \'c1\' at'
        self.assertTrue(str(root['c1']).startswith(expected))

        # After accessing 'c1', it is cached as well:
        self.check_output("""\
        [('c1', <Node object 'c1' at ...>),
        ('c2', <Node object 'c2' at ...>)]
        """, str(sorted(root.cache.items())))

        # Invalidate plumbing removes item from cache
        root.invalidate(key='c1')
        self.assertEqual(list(root.cache.keys()), ['c2'])

        root.invalidate()
        self.assertEqual(root.cache, {})

        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
        ))

        # Test invalidation plumbing hook with missing cache values
        root['x1'] = Node()
        root['x2'] = Node()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: x1\n'
            '  <class \'node.tests.test_cache.Node\'>: x2\n'
        ))

        self.check_output("""\
        [('x1', <Node object 'x1' at ...>),
        ('x2', <Node object 'x2' at ...>)]
        """, str(sorted(root.cache.items())))

        del root.cache['x1']
        del root.cache['x2']

        root.invalidate(key='x1')
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
            '  <class \'node.tests.test_cache.Node\'>: x2\n'
        ))

        del root.cache['x2']
        root.invalidate()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_cache.Node\'>: None\n'
        ))

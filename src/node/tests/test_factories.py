from node.behaviors import ChildFactory
from node.behaviors import DefaultInit
from node.behaviors import FixedChildren
from node.behaviors import MappingNode
from node.behaviors import Node
from node.behaviors import OdictStorage
from node.behaviors import WildcardFactory
from node.behaviors.factories import _wildcard_pattern_occurrences
from node.behaviors.factories import _wildcard_patterns_by_specificity
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing


@plumbing(DefaultInit, Node)
class Factory(object):
    pass


@plumbing(Node)
class LegacyFactory(object):
    pass


class TestFactories(NodeTestCase):

    def test_ChildFactory(self):
        @plumbing(MappingNode, ChildFactory, OdictStorage)
        class ChildFactoryNode(object):
            factories = odict([
                ('factory', Factory),
                ('legacy', LegacyFactory)
            ])

        node = ChildFactoryNode()
        self.assertEqual(list(node.keys()), ['factory', 'legacy'])
        self.assertTrue(isinstance(node['factory'], Factory))
        self.assertTrue(isinstance(node['legacy'], LegacyFactory))

    def test_FixedChildren(self):
        @plumbing(MappingNode, FixedChildren)
        class FixedChildrenNode(object):
            factories = odict([
                ('factory', Factory),
                ('legacy', LegacyFactory)
            ])

        node = FixedChildrenNode()
        self.assertEqual(list(node.keys()), ['factory', 'legacy'])
        self.assertTrue(isinstance(node['factory'], Factory))
        self.assertTrue(isinstance(node['legacy'], LegacyFactory))
        self.assertTrue(node['factory'] is node['factory'])

        with self.assertRaises(NotImplementedError) as arc:
            del node['factory']
        self.assertEqual(str(arc.exception), 'read-only')

        with self.assertRaises(NotImplementedError) as arc:
            node['factory'] = Factory()
        self.assertEqual(str(arc.exception), 'read-only')

        @plumbing(MappingNode, FixedChildren)
        class LegacyFixedChildrenNode(object):
            fixed_children_factories = odict([
                ('factory', Factory),
                ('legacy', LegacyFactory)
            ])

        node = LegacyFixedChildrenNode()
        self.assertEqual(list(node.keys()), ['factory', 'legacy'])

        # B/C interface violation
        @plumbing(MappingNode, FixedChildren)
        class LegacyFixedChildrenNode(object):
            fixed_children_factories = (
                ('factory', Factory),
                ('legacy', LegacyFactory)
            )

        node = LegacyFixedChildrenNode()
        self.assertEqual(list(node.keys()), ['factory', 'legacy'])

    def test_WildcardFactory(self):
        self.assertEqual(_wildcard_pattern_occurrences('abc'), (3, 0, 0, 0))
        self.assertEqual(_wildcard_pattern_occurrences('*a*b*'), (5, 3, 0, 0))
        self.assertEqual(_wildcard_pattern_occurrences('?a?b?'), (5, 0, 3, 0))
        self.assertEqual(
            _wildcard_pattern_occurrences('[a-z]a[abc]b[!abc]'),
            (5, 0, 0, 3)
        )
        self.assertEqual(
            _wildcard_pattern_occurrences('*?[a-z]a*[abc]b?[!abc]?*'),
            (11, 3, 3, 3)
        )
        with self.assertRaises(ValueError):
            _wildcard_pattern_occurrences('*?[')
        with self.assertRaises(ValueError):
            _wildcard_pattern_occurrences('[*?')

        # specificity 1
        self.assertEqual(
            _wildcard_patterns_by_specificity(('a', 'aa', 'aaa')),
            ('aaa', 'aa', 'a')
        )
        # specificity 2
        self.assertEqual(
            _wildcard_patterns_by_specificity(('[a-z]', '[abc][abc]')),
            ('[abc][abc]', '[a-z]')
        )
        # specificity 3
        self.assertEqual(
            _wildcard_patterns_by_specificity(('?', '??')),
            ('??', '?')
        )
        self.assertEqual(
            _wildcard_patterns_by_specificity(
                ('?', '??', '[a-z]', '[abc][abc]')
            ),
            ('[abc][abc]', '[a-z]', '??', '?')
        )
        self.assertEqual(
            _wildcard_patterns_by_specificity(
                ('?', '??', '[a-z]', '[abc][abc]', '?[a-z]', '??[a-z]', '?[a-z][a-z]')
            ),
            ('[abc][abc]', '[a-z]', '?[a-z][a-z]', '??[a-z]', '?[a-z]', '??', '?')
        )
        # specificity 4
        self.assertEqual(
            _wildcard_patterns_by_specificity(('*', '*.*')),
            ('*.*', '*')
        )

        self.assertEqual(
            _wildcard_patterns_by_specificity(
                ('*', '*bc', '?bc', '[xyz]bc', 'abc')
            ),
            ('abc', '[xyz]bc', '?bc', '*bc', '*')
        )

        @plumbing(WildcardFactory)
        class WildCardFactoryNode(object):
            factories = {
                '*': 'default_factory'
            }

from node.behaviors import ChildFactory
from node.behaviors import DefaultInit
from node.behaviors import FixedChildren
from node.behaviors import MappingNode
from node.behaviors import Node
from node.behaviors import OdictStorage
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
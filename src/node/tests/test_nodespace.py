from node.behaviors import DefaultInit
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import Nodespaces
from node.behaviors import OdictStorage
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    MappingAdopt,
    Nodespaces,
    MappingNode,
    OdictStorage)
class NodespacesNode(odict):
    pass


@plumbing(
    MappingAdopt,
    MappingNode,
    DefaultInit,
    OdictStorage)
class SomeNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestNodespace(NodeTestCase):

    def test_Nodespaces(self):
        node = NodespacesNode()
        self.assertTrue(isinstance(node.nodespaces, odict))
        self.assertEqual(node.nodespaces['__children__'], node)

        child = node['__children__']['child'] = SomeNode()
        self.assertEqual(node['child'], child)

        self.assertTrue(node['__children__']['child'] is node['child'])

        foo = node['__foo__'] = SomeNode()
        self.assertEqual(node['__foo__'], foo)

        child = node['__foo__']['child'] = SomeNode()
        self.assertEqual(node['__foo__']['child'], child)

        self.assertFalse(node['__foo__']['child'] is node['child'])

        self.assertEqual(len(node.nodespaces), 2)
        self.assertEqual(node.nodespaces['__children__'], node)
        self.assertEqual(node.nodespaces['__foo__'], foo)

        with self.assertRaises(KeyError) as arc:
            node['__inexistent__']
        self.assertEqual(str(arc.exception), '\'__inexistent__\'')

        with self.assertRaises(KeyError) as arc:
            node['inexistent']
        self.assertEqual(str(arc.exception), '\'inexistent\'')

        del node['child']
        self.assertEqual(node.keys(), [])

        self.assertEqual(list(node['__foo__'].keys()), ['child'])

        del node['__foo__']
        self.assertEqual(len(node.nodespaces), 1)

        self.assertEqual(list(node.nodespaces.keys()), ['__children__'])

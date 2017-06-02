from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Adopt,
    Nodespaces,
    Nodify,
    OdictStorage)
class NodespacesNode(odict):
    pass


@plumbing(
    Adopt,
    Nodify,
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

        def __getitem__fails():
            node['__inexistent__']
        err = self.expect_error(KeyError, __getitem__fails)
        self.assertEqual(str(err), '\'__inexistent__\'')

        def __getitem__fails2():
            node['inexistent']
        err = self.expect_error(KeyError, __getitem__fails2)
        self.assertEqual(str(err), '\'inexistent\'')

        del node['child']
        self.assertEqual(node.keys(), [])

        self.assertEqual(list(node['__foo__'].keys()), ['child'])

        del node['__foo__']
        self.assertEqual(len(node.nodespaces), 1)

        self.assertEqual(list(node.nodespaces.keys()), ['__children__'])

from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors import Reference
from node.behaviors.reference import NodeIndex
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface.common.mapping import IReadMapping
import uuid


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Adopt,
    Reference,
    DefaultInit,
    Nodify,
    OdictStorage)
class ReferenceNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestReference(NodeTestCase):

    def test_node_index(self):
        # Tree node index
        node = ReferenceNode()
        self.assertTrue(isinstance(node.index, NodeIndex))
        self.assertTrue(IReadMapping.providedBy(node.index))
        self.assertEqual(node.index[node.uuid], node)
        self.assertEqual(node.index.get(node.uuid), node)
        self.assertTrue(node.uuid in node.index)
        self.assertEqual(len(node.index._index), 1)

    def test_containment(self):
        # Add some children and check node containment stuff
        node = ReferenceNode(name='root')

        node['child'] = ReferenceNode()
        self.assertEqual(node['child'].path, ['root', 'child'])
        self.assertTrue(node.index._index is node['child'].index._index)
        self.assertEqual(len(node.index._index), 2)

        node['child']['sub'] = ReferenceNode()
        self.assertEqual(len(node.index._index), 3)

        node['child']['sub2'] = ReferenceNode()
        self.assertEqual(len(node.index._index), 4)

        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_reference.ReferenceNode'>: root\n"
            "  <class 'node.tests.test_reference.ReferenceNode'>: child\n"
            "    <class 'node.tests.test_reference.ReferenceNode'>: sub\n"
            "    <class 'node.tests.test_reference.ReferenceNode'>: sub2\n"
        ))

        # Adding in indexed Node with same uuid or the same node twice fails
        child = node['child']

        def __setitem__fails():
            node['child2'] = child
        err = self.expect_error(ValueError, __setitem__fails)
        self.assertEqual(str(err), 'Node with uuid already exists')

    def test_uuid(self):
        # Check UUID stuff
        node = ReferenceNode(name='root')
        node['child'] = ReferenceNode()
        node['child']['sub'] = ReferenceNode()
        node['child']['sub2'] = ReferenceNode()

        uid = node['child']['sub'].uuid
        self.assertTrue(isinstance(uid, uuid.UUID))
        self.assertEqual(node.node(uid).path, ['root', 'child', 'sub'])

        def set_uuid_fails():
            node.uuid = uid
        err = self.expect_error(ValueError, set_uuid_fails)
        expected = 'Given uuid was already used for another Node'
        self.assertEqual(str(err), expected)

        new_uid = uuid.uuid4()
        node.uuid = new_uid
        self.assertEqual(node['child'].node(new_uid).path, ['root'])
        self.assertEqual(len(node._index.keys()), 4)

        # Store the uuids of the nodes which are expected to be deleted from
        # index if child is deleted
        delindexes = [
            int(node['child'].uuid),
            int(node['child']['sub'].uuid),
            int(node['child']['sub2'].uuid),
        ]

        # Read the uuid index and check containment in index
        iuuids = node._index.keys()
        self.assertEqual(len(iuuids), 4)
        self.assertTrue(delindexes[0] in iuuids)
        self.assertTrue(delindexes[1] in iuuids)
        self.assertTrue(delindexes[2] in iuuids)

        # Delete child. All checked uuids above must be deleted from index
        del node['child']
        self.assertEqual(list(node.keys()), [])

        uuids = node._index.keys()
        self.assertEqual(len(uuids), 1)
        self.assertTrue(node.index[node.uuid] is node)
        self.assertFalse(delindexes[0] in uuids)
        self.assertFalse(delindexes[1] in uuids)
        self.assertFalse(delindexes[2] in uuids)
        self.assertEqual(node.treerepr(), (
            "<class 'node.tests.test_reference.ReferenceNode'>: root\n"
        ))

        node['child'] = ReferenceNode()
        node['child'].allow_non_node_childs = True
        node['child']['foo'] = 1
        del node['child']

from node.behaviors import DefaultInit
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import OdictStorage
from node.behaviors import UnicodeAware
from node.behaviors import UUIDAware
from node.tests import NodeTestCase
from plumber import plumbing
import uuid


class TestCommon(NodeTestCase):

    def test_UnicodeAware(self):
        @plumbing(MappingNode, UnicodeAware, OdictStorage)
        class UnicodeNode(object):
            pass

        node = UnicodeNode()
        node['foo'] = UnicodeNode()
        self.assertEqual(list(node.keys()), [u'foo'])

        node['bar'] = 'bar'
        self.assertEqual(
            node.items(),
            [(u'foo', node['foo']), (u'bar', u'bar')]
        )

        self.assertTrue(isinstance(node['foo'], UnicodeNode))

        del node['bar']
        self.assertEqual(list(node.keys()), [u'foo'])

    def test_UUIDAware(self):
        # Create a uid aware node. ``copy`` is not supported on UUIDAware node
        # trees, ``deepcopy`` must be used
        @plumbing(
            MappingAdopt,
            DefaultInit,
            MappingNode,
            OdictStorage,
            UUIDAware)
        class UUIDNode(object):
            pass

        # UUID is set at init time
        root = UUIDNode(name='root')
        self.assertTrue(isinstance(root.uuid, uuid.UUID))

        # Shallow ``copy`` is prohibited for UUID aware nodes
        with self.assertRaises(RuntimeError) as arc:
            root.copy()
        exp = 'Shallow copy useless on UUID aware node trees, use deepcopy.'
        self.assertEqual(str(arc.exception), exp)

        # On ``deepcopy``, a new uid gets set:
        root_cp = root.deepcopy()
        self.assertFalse(root is root_cp)
        self.assertFalse(root.uuid == root_cp.uuid)

        # Create children, copy tree and check if all uuids have changed
        c1 = root['c1'] = UUIDNode()
        c1['s1'] = UUIDNode()
        self.assertEqual(root.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
            "  <class 'node.tests.test_common.UUIDNode'>: c1\n"
            "    <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        root_cp = root.deepcopy()
        self.assertEqual(root_cp.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
            "  <class 'node.tests.test_common.UUIDNode'>: c1\n"
            "    <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        self.assertFalse(root.uuid == root_cp.uuid)
        self.assertFalse(root['c1'].uuid == root_cp['c1'].uuid)
        self.assertFalse(root['c1']['s1'].uuid == root_cp['c1']['s1'].uuid)

        # When detaching part of a tree, uid's are not changed
        c1_uid = root['c1'].uuid
        s1_uid = root['c1']['s1'].uuid
        detached = root.detach('c1')

        self.assertEqual(root.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
        ))

        self.assertEqual(detached.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: c1\n"
            "  <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        self.assertTrue(c1_uid == detached.uuid)
        self.assertTrue(s1_uid == detached['s1'].uuid)

        # uuid not gets overwritten on __init__ if already set
        UUIDNode.uuid = uuid.UUID('3252e869-72cf-4426-9e34-abbc3cbe3af0')
        uuid_node = UUIDNode()
        self.assertEqual(uuid_node.uuid, UUIDNode.uuid)

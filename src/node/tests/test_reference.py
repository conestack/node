from node.behaviors import DefaultInit
from node.behaviors import IndexViolationError
from node.behaviors import ListStorage
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import MappingReference
from node.behaviors import Node
from node.behaviors import NodeIndex
from node.behaviors import NodeReference
from node.behaviors import OdictStorage
from node.behaviors import SequenceAdopt
from node.behaviors import SequenceNode
from node.behaviors import SequenceReference
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface.common.mapping import IReadMapping
import uuid


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    DefaultInit,
    Node)
class NoReferenceNode(object):
    pass


@plumbing(
    NodeReference,
    DefaultInit,
    Node)
class ReferenceNode(object):
    pass


@plumbing(
    MappingAdopt,
    MappingReference,
    DefaultInit,
    MappingNode,
    OdictStorage)
class ReferenceMappingNode(object):
    pass


@plumbing(
    SequenceAdopt,
    SequenceReference,
    DefaultInit,
    SequenceNode,
    ListStorage)
class ReferenceSequenceNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestReference(NodeTestCase):

    def test_node_index(self):
        # Tree node index
        node = ReferenceMappingNode()
        self.assertTrue(isinstance(node.index, NodeIndex))
        self.assertTrue(IReadMapping.providedBy(node.index))
        self.assertEqual(node.index[node.uuid], node)
        self.assertEqual(node.index.get(node.uuid), node)
        self.assertTrue(node.uuid in node.index)
        self.assertEqual(len(node.index._index), 1)

    def test_adding(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.insert(0, ReferenceNode())
        sequence.insert(0, NoReferenceNode())
        node['sequence'] = sequence

        self.assertEqual(len(node.index._index), 6)

        self.assertTrue(node._index is mapping._index)
        self.assertTrue(node._index is mapping['ref']._index)
        self.assertTrue(node._index is sequence._index)
        self.assertTrue(node._index is sequence[1]._index)

        self.assertTrue(node.node(mapping.uuid) is mapping)
        self.assertTrue(node.node(mapping['ref'].uuid) is mapping['ref'])

        self.assertTrue(node.node(sequence.uuid) is sequence)
        self.assertTrue(node.node(sequence['1'].uuid) is sequence['1'])

        self.assertFalse(mapping['noref'] in node._index.values())
        self.assertFalse(sequence['0'] in node._index.values())

    def test_overwrite(self):
        node = ReferenceMappingNode(name='root')
        node['mapping'] = ReferenceMappingNode()
        node['mapping']['ref'] = ReferenceNode()
        node['sequence'] = ReferenceSequenceNode()
        node['sequence'].append(ReferenceNode())

        self.assertEqual(len(node._index), 5)

        invalid = ReferenceNode()
        invalid.uuid = node.uuid

        with self.assertRaises(IndexViolationError) as arc:
            node['mapping']['invalid'] = invalid
        self.checkOutput("""
        Index Violation: Node with uuid(s) already exist in tree
          * ...
        """, repr(arc.exception))

        with self.assertRaises(IndexViolationError):
            node['mapping'] = node['mapping']
        with self.assertRaises(IndexViolationError):
            node['mapping'] = node['sequence']
        with self.assertRaises(IndexViolationError):
            node['sequence'].append(invalid)
        with self.assertRaises(IndexViolationError):
            node['sequence'].insert(0, invalid)
        with self.assertRaises(IndexViolationError):
            node['sequence']['0'] = node['mapping']['ref']

        self.assertEqual(len(node._index), 5)

    def test_detach(self):
        node = ReferenceMappingNode(name='root')
        node['mapping'] = ReferenceMappingNode()
        node['mapping']['ref'] = ReferenceNode()
        node['sequence'] = ReferenceSequenceNode()
        node['sequence'].insert(0, ReferenceNode())

        self.assertEqual(len(node._index), 5)

        mapping = node.detach('mapping')
        self.assertEqual(len(mapping._index), 2)
        self.assertEqual(len(node._index), 3)

        ref = node['sequence'].detach(0)
        self.assertEqual(len(ref._index), 1)
        self.assertEqual(len(node._index), 2)

    def test_clear(self):
        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['mapping'] = ReferenceMappingNode()
        mapping['sequence'] = ReferenceSequenceNode()
        self.assertEqual(len(mapping._index), 4)

        mapping.clear()
        self.assertEqual(len(mapping._index), 1)

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(ReferenceMappingNode())
        sequence.append(ReferenceSequenceNode())
        self.assertEqual(len(sequence._index), 4)

        sequence.clear()
        self.assertEqual(len(sequence._index), 1)

    def test_uuid(self):
        node = ReferenceMappingNode(name='root')
        node['mapping'] = ReferenceMappingNode()
        node['mapping']['ref'] = ReferenceNode()
        node['sequence'] = ReferenceSequenceNode()
        node['sequence'].insert(0, ReferenceNode())

        uid = node['mapping']['ref'].uuid
        self.assertTrue(isinstance(uid, uuid.UUID))
        self.assertEqual(node.node(uid).path, ['root', 'mapping', 'ref'])

        uid = node['sequence'][0].uuid
        self.assertTrue(isinstance(uid, uuid.UUID))
        self.assertEqual(node.node(uid).path, ['root', 'sequence', '0'])

        with self.assertRaises(IndexViolationError) as arc:
            node.uuid = uid
        self.assertEqual(
            arc.exception.message,
            'Given uuid was already used for another Node'
        )

        new_uid = uuid.uuid4()
        node.uuid = new_uid
        self.assertEqual(node['sequence'].node(new_uid).path, ['root'])
        self.assertEqual(len(node._index.keys()), 5)

    def test_delete(self):
        node = ReferenceMappingNode(name='root')
        node['mapping'] = ReferenceMappingNode()
        node['mapping']['ref'] = ReferenceNode()
        node['sequence'] = ReferenceSequenceNode()
        node['sequence'].insert(0, ReferenceNode())

        delindexes = [
            int(node['mapping'].uuid),
            int(node['mapping']['ref'].uuid),
            int(node['sequence'].uuid),
            int(node['sequence']['0'].uuid)
        ]

        index = node._index
        self.assertEqual(len(index), 5)
        self.assertTrue(delindexes[0] in index)
        self.assertTrue(delindexes[1] in index)
        self.assertTrue(delindexes[2] in index)
        self.assertTrue(delindexes[3] in index)

        del node['mapping']
        del node['sequence']
        self.assertEqual(list(node.keys()), [])

        self.assertEqual(len(node._index), 1)
        self.assertTrue(node.index[node.uuid] is node)

        node.child_constraints = None
        node['foo'] = 1
        self.assertEqual(len(node._index), 1)

        del node['foo']
        self.assertEqual(len(node._index), 1)

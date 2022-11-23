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
from node.interfaces import IMappingReference
from node.interfaces import INodeReference
from node.interfaces import ISequenceReference
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

    def test_interfaces(self):
        self.assertTrue(INodeReference.providedBy(ReferenceNode()))
        self.assertTrue(IMappingReference.providedBy(ReferenceMappingNode()))
        self.assertTrue(ISequenceReference.providedBy(ReferenceSequenceNode()))

    def test_index(self):
        # Tree node index
        node = ReferenceNode()
        self.assertTrue(isinstance(node.index, NodeIndex))
        self.assertTrue(IReadMapping.providedBy(node.index))
        self.assertEqual(node.index[node.uuid], node)
        self.assertEqual(node.index.get(node.uuid), node)
        self.assertTrue(node.uuid in node.index)
        self.assertTrue(node._index is node.index._index)
        self.assertEqual(len(node._index), 1)

    def test_IndexViolationError(self):
        uid = uuid.UUID('c7022c39-aac3-42c8-b86e-6daddefa3425')
        err = IndexViolationError('Message', [int(uid)])
        self.assertEqual(err.message, 'Message')
        self.assertEqual(err.colliding, [uid])
        self.assertEqual(repr(err).split('\n'), [
            'Index Violation: Message',
            '  * c7022c39-aac3-42c8-b86e-6daddefa3425'
        ])

    def test_uuid(self):
        node = ReferenceNode(name='root')
        node_uuid = node.uuid
        self.assertIsInstance(node_uuid, uuid.UUID)
        self.assertTrue(node.index[int(node_uuid)] is node)

        node.uuid = uuid.uuid4()
        self.assertFalse(int(node_uuid) in node.index)
        self.assertTrue(int(node.uuid) in node.index)

        conflicting_uuid = uuid.uuid4()
        node._index[int(conflicting_uuid)] = ReferenceNode()
        with self.assertRaises(IndexViolationError) as arc:
            node.uuid = conflicting_uuid
        self.assertEqual(
            arc.exception.message,
            'Given uuid was already used for another Node'
        )
        self.assertEqual(arc.exception.colliding, [conflicting_uuid])

    def test_node(self):
        node = ReferenceNode(name='root')
        self.assertTrue(node.node(node.uuid) is node)
        self.assertEqual(node.node(uuid.uuid4()), None)

    def test__referencable_child_nodes(self):
        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        self.assertEqual(
            [it for it in mapping._referencable_child_nodes],
            [mapping['ref']]
        )

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(NoReferenceNode())
        self.assertEqual(
            [it for it in sequence._referencable_child_nodes],
            [sequence[0]]
        )

    def test__recursiv_reference_keys(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(NoReferenceNode())
        node['sequence'] = sequence

        self.assertEqual(node._recursiv_reference_keys, [
            int(node.uuid),
            int(mapping.uuid),
            int(mapping['ref'].uuid),
            int(sequence.uuid),
            int(sequence[0].uuid),
        ])

    def test__init_reference_index(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(NoReferenceNode())
        node['sequence'] = sequence

        node._index = dict()
        node._init_reference_index()
        self.assertEqual(len(node._index), 5)
        self.assertTrue(int(node.uuid) in node._index)
        self.assertTrue(int(mapping.uuid) in node._index)
        self.assertTrue(int(mapping['ref'].uuid) in node._index)
        self.assertTrue(int(sequence.uuid) in node._index)
        self.assertTrue(int(sequence[0].uuid) in node._index)

    def test__update_reference_index(self):
        node = ReferenceMappingNode(name='root')
        node['mapping'] = ReferenceMappingNode()
        node['mapping']['ref'] = ReferenceNode()
        node['mapping']['noref'] = NoReferenceNode()
        node['sequence'] = ReferenceSequenceNode()
        node['sequence'].append(ReferenceNode())
        node['sequence'].append(NoReferenceNode())
        self.assertEqual(len(node._index), 5)

        node._update_reference_index(NoReferenceNode())
        self.assertEqual(len(node._index), 5)

        new = ReferenceMappingNode()
        new['ref'] = ReferenceNode()
        new['noref'] = NoReferenceNode()

        node._update_reference_index(new)
        self.assertEqual(len(node._index), 7)

        self.assertTrue(new._index is node._index)
        self.assertTrue(new['ref']._index is node._index)

        invalid = ReferenceMappingNode()
        invalid.uuid = node.uuid
        with self.assertRaises(IndexViolationError) as arc:
            node._update_reference_index(invalid)
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])

        valid = ReferenceMappingNode()
        valid['invalid'] = ReferenceNode()
        valid['invalid'].uuid = node.uuid
        with self.assertRaises(IndexViolationError) as arc:
            node._update_reference_index(valid)
        self.assertEqual(arc.exception.colliding, [node.uuid])

    def test__reduce_reference_index(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(NoReferenceNode())
        node['sequence'] = sequence

        self.assertEqual(len(node._index), 5)
        self.assertTrue(int(node.uuid) in node._index)
        self.assertTrue(int(mapping.uuid) in node._index)
        self.assertTrue(int(mapping['ref'].uuid) in node._index)
        self.assertTrue(int(sequence.uuid) in node._index)
        self.assertTrue(int(sequence[0].uuid) in node._index)

        node._reduce_reference_index(mapping)
        self.assertEqual(len(node._index), 3)
        self.assertTrue(int(node.uuid) in node._index)
        self.assertTrue(int(sequence.uuid) in node._index)
        self.assertTrue(int(sequence[0].uuid) in node._index)

        node._reduce_reference_index(sequence)
        self.assertEqual(len(node._index), 1)
        self.assertTrue(int(node.uuid) in node._index)

    def test_adding(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.insert(0, ReferenceNode())
        sequence.insert(0, NoReferenceNode())
        node['sequence'] = sequence

        self.assertEqual(len(node._index), 6)

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

        with self.assertRaises(IndexViolationError) as arc:
            mapping['invalid'] = mapping['ref']
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 6)
        self.assertEqual(mapping.keys(), ['ref', 'noref'])

        with self.assertRaises(IndexViolationError) as arc:
            sequence[0] = sequence[1]
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 6)
        self.assertEqual(len(sequence), 3)

        with self.assertRaises(IndexViolationError) as arc:
            sequence.append(sequence[1])
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 6)
        self.assertEqual(len(sequence), 3)

        with self.assertRaises(IndexViolationError) as arc:
            sequence.insert(0, sequence[1])
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 6)
        self.assertEqual(len(sequence), 3)

        invalid = ReferenceNode()
        invalid.uuid = node.uuid
        with self.assertRaises(IndexViolationError) as arc:
            mapping['invalid'] = invalid
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 6)

        with self.assertRaises(IndexViolationError) as arc:
            sequence[0] = invalid
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 6)

        with self.assertRaises(IndexViolationError) as arc:
            sequence.insert(0, invalid)
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 6)

        with self.assertRaises(IndexViolationError) as arc:
            sequence.append(invalid)
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 6)

    def test_overwrite(self):
        node = ReferenceMappingNode(name='root')

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        node['mapping'] = mapping

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.insert(1, NoReferenceNode())
        node['sequence'] = sequence

        self.assertEqual(len(node._index), 5)

        with self.assertRaises(IndexViolationError) as arc:
            mapping['ref'] = mapping['ref']
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 5)

        with self.assertRaises(IndexViolationError) as arc:
            sequence['0'] = sequence['0']
        self.assertEqual(
            arc.exception.message,
            'Given node is already member of tree.'
        )
        self.assertEqual(len(node._index), 5)

        new_mapping = ReferenceMappingNode()
        new_mapping['ref'] = ReferenceNode()
        new_mapping['noref'] = NoReferenceNode()
        node['mapping'] = new_mapping

        self.assertEqual(len(node._index), 5)
        self.assertFalse(int(mapping.uuid) in node._index)
        self.assertFalse(int(mapping['ref'].uuid) in node._index)
        self.assertTrue(int(new_mapping.uuid) in node._index)
        self.assertTrue(int(new_mapping['ref'].uuid) in node._index)

        new_sequence = ReferenceSequenceNode()
        new_sequence.append(ReferenceNode())
        new_sequence.insert(1, NoReferenceNode())
        node['sequence'] = new_sequence

        self.assertEqual(len(node._index), 5)
        self.assertFalse(int(sequence.uuid) in node._index)
        self.assertFalse(int(sequence[0].uuid) in node._index)
        self.assertTrue(int(new_sequence.uuid) in node._index)
        self.assertTrue(int(new_sequence[0].uuid) in node._index)

        old_sequence_child = node['sequence']['0']
        new_sequence_child = node['sequence']['0'] = ReferenceNode()
        self.assertEqual(len(node._index), 5)
        self.assertFalse(int(old_sequence_child.uuid) in node._index)
        self.assertTrue(int(new_sequence_child.uuid) in node._index)

        invalid_mapping = ReferenceMappingNode()
        invalid_mapping['ref'] = ReferenceNode()
        invalid_mapping['ref'].uuid = node.uuid

        with self.assertRaises(IndexViolationError) as arc:
            node['mapping'] = invalid_mapping
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )

        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 5)

        with self.assertRaises(IndexViolationError) as arc:
            node['mapping']['noref'] = invalid_mapping
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )

        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 5)

        invalid_sequence = ReferenceSequenceNode()
        invalid_sequence.append(ReferenceNode())
        invalid_sequence[0].uuid = node.uuid

        with self.assertRaises(IndexViolationError) as arc:
            node['sequence'] = invalid_sequence
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 5)

        invalid_sequence_child = ReferenceNode()
        invalid_sequence_child.uuid = node.uuid

        with self.assertRaises(IndexViolationError) as arc:
            node['sequence'][0] = invalid_sequence_child
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
        self.assertEqual(len(node._index), 5)

        with self.assertRaises(IndexViolationError) as arc:
            node['sequence'][1] = invalid_sequence_child
        self.assertEqual(
            arc.exception.message,
            'Given node or members of it provide uuid(s) colliding with own index.'
        )
        self.assertEqual(arc.exception.colliding, [node.uuid])
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

    def test_subtree(self):
        node = ReferenceMappingNode(name='root')
        self.assertEqual(len(node._index), 1)

        mapping = ReferenceMappingNode()
        mapping['ref'] = ReferenceNode()
        mapping['noref'] = NoReferenceNode()
        self.assertEqual(len(mapping._index), 2)
        self.assertFalse(node._index is mapping._index)

        sequence = ReferenceSequenceNode()
        sequence.append(ReferenceNode())
        sequence.append(NoReferenceNode())
        self.assertEqual(len(sequence._index), 2)
        self.assertFalse(node._index is sequence._index)

        node['mapping'] = mapping
        node['sequence'] = sequence
        self.assertTrue(node._index is mapping._index)
        self.assertTrue(node._index is mapping['ref']._index)
        self.assertTrue(node._index is sequence._index)
        self.assertTrue(node._index is sequence[0]._index)
        self.assertEqual(len(sequence._index), 5)

        node.detach('mapping')
        node.detach('sequence')
        self.assertFalse(node._index is mapping._index)
        self.assertFalse(node._index is sequence._index)
        self.assertTrue(mapping._index is mapping['ref']._index)
        self.assertTrue(sequence._index is sequence[0]._index)
        self.assertEqual(len(node._index), 1)
        self.assertEqual(len(mapping._index), 2)
        self.assertEqual(len(sequence._index), 2)

    def test_BC_imports(self):
        from node.behaviors import Reference
        self.assertTrue(Reference is MappingReference)

        from node.interfaces import IReference
        self.assertTrue(IReference is IMappingReference)

from node.behaviors import DictStorage
from node.behaviors import ListStorage
from node.behaviors import MappingStorage
from node.behaviors import OdictStorage
from node.behaviors import SequenceStorage
from node.interfaces import IMappingStorage
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(MappingStorage)
class MappingStorageObject(object):
    pass


@plumbing(DictStorage)
class DictStorageObject(object):
    pass


@plumbing(OdictStorage)
class OdictStorageObject(object):
    pass


@plumbing(SequenceStorage)
class SequenceStorageObject(object):
    pass


@plumbing(ListStorage)
class ListStorageObject(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestStorage(NodeTestCase):

    def test_MappingStorage(self):
        obj = MappingStorageObject()
        self.assertTrue(IMappingStorage.providedBy(obj))

        with self.assertRaises(NotImplementedError) as arc:
            obj.storage
        expected = 'Abstract ``MappingStorage`` does not implement ``storage``'
        self.assertEqual(str(arc.exception), expected)

    def test_DictStorage(self):
        obj = DictStorageObject()
        self.assertEqual(obj.storage, {})

        obj['foo'] = 'foo'
        self.assertEqual(obj.storage, {'foo': 'foo'})
        self.assertEqual(obj['foo'], 'foo')
        self.assertEqual([key for key in obj], ['foo'])

        del obj['foo']
        self.assertEqual(obj.storage, {})

    def test_OdictStorage(self):
        obj = OdictStorageObject()
        self.assertEqual(obj.storage, odict())

        obj['foo'] = 'foo'
        self.assertEqual(obj.storage, odict([('foo', 'foo')]))
        self.assertEqual(obj['foo'], 'foo')
        self.assertEqual([key for key in obj], ['foo'])

        del obj['foo']
        self.assertEqual(obj.storage, odict())

    def test_SequenceStorage(self):
        obj = SequenceStorageObject()

        with self.assertRaises(NotImplementedError) as arc:
            obj.storage
        expected = 'Abstract ``SequenceStorage`` does not implement ``storage``'
        self.assertEqual(str(arc.exception), expected)

    def test_ListStorage(self):
        lseq = ListStorageObject()
        self.assertEqual(lseq.storage, [])

        # insert
        lseq.insert(0, 0)
        self.assertEqual(lseq.storage, [0])

        # __setitem__
        lseq[0] = 1
        self.assertEqual(lseq.storage, [1])

        # __len__
        self.assertEqual(len(lseq), 1)

        # __getitem__
        self.assertEqual(lseq[0], 1)
        with self.assertRaises(IndexError):
            lseq[1]

        # __delitem__
        del lseq[0]
        self.assertEqual(lseq.storage, [])
        with self.assertRaises(IndexError):
            del lseq[0]

    def test_BC_imports(self):
        from node.behaviors import Storage
        self.assertTrue(Storage is MappingStorage)

        from node.interfaces import IStorage
        self.assertTrue(IStorage is IMappingStorage)

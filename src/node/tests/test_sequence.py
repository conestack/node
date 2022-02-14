from node.base import BaseNode
from node.behaviors import ListStorage
from node.behaviors import MutableSequence
from node.behaviors import Sequence
from node.behaviors import SequenceNode as SequenceNodeBehavior
from node.interfaces import IMappingNode
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import Interface


class TestSequence(NodeTestCase):

    def test_Sequence(self):
        @plumbing(Sequence)
        class AbstractTestSequence(object):
            pass

        seq = AbstractTestSequence()

        # __len__
        with self.assertRaises(NotImplementedError):
            len(seq)

        # __getitem__
        with self.assertRaises(NotImplementedError):
            seq[0]

        @plumbing(Sequence)
        class TestSequence(object):
            def __init__(self, data):
                self.data = data

            def __len__(self):
                return len(self.data)

            def __getitem__(self, index):
                return self.data[index]

        seq = TestSequence([1, 2, 3])

        # __len__
        self.assertEqual(len(seq), 3)

        # __getitem__
        self.assertEqual(seq[0], 1)
        with self.assertRaises(IndexError):
            seq[3]

        # __contains__
        self.assertTrue(1 in seq)
        self.assertFalse(4 in seq)

        # __iter__
        self.assertEqual(list(iter(seq)), [1, 2, 3])

        # __reversed__
        self.assertEqual(list(reversed(seq)), [3, 2, 1])

        # count
        self.assertEqual(seq.count(1), 1)
        self.assertEqual(seq.count(4), 0)

        # index
        self.assertEquals(seq.index(2), 1)
        with self.assertRaises(ValueError):
            seq.index(4)

    def test_MutableSequence(self):
        @plumbing(MutableSequence)
        class AbstractTestMutableSequence(object):
            pass

        mseq = AbstractTestMutableSequence()

        # __setitem__
        with self.assertRaises(NotImplementedError):
            mseq[0] = 0

        # __delitem__
        with self.assertRaises(NotImplementedError):
            del mseq[0]

        # insert
        with self.assertRaises(NotImplementedError):
            mseq.insert(0, 0)

        @plumbing(MutableSequence)
        class TestMutableSequence(object):
            def __init__(self, data):
                self.data = data

            def __len__(self):
                return len(self.data)

            def __getitem__(self, index):
                return self.data[index]

            def __setitem__(self, index, value):
                self.data[index] = value

            def __delitem__(self, index):
                del self.data[index]

            def insert(self, index, value):
                self.data.insert(index, value)

        mseq = TestMutableSequence([1, 2, 3])

        # __setitem__
        mseq[2] = 4
        self.assertEqual(mseq.data, [1, 2, 4])

        # __delitem__
        del mseq[2]
        self.assertEqual(mseq.data, [1, 2])

        # insert
        mseq.insert(2, 3)
        self.assertEqual(mseq.data, [1, 2, 3])

        # __iadd__
        mseq += [4]
        self.assertEqual(mseq.data, [1, 2, 3, 4])

        # append
        mseq.append(5)
        self.assertEqual(mseq.data, [1, 2, 3, 4, 5])

        # extend
        mseq.extend([6, 7])
        self.assertEqual(mseq.data, [1, 2, 3, 4, 5, 6, 7])

        # pop
        value = mseq.pop()
        self.assertEqual(value, 7)
        self.assertEqual(mseq.data, [1, 2, 3, 4, 5, 6])

        # remove
        mseq.remove(6)
        self.assertEqual(mseq.data, [1, 2, 3, 4, 5])

        # reverse
        mseq.reverse()
        self.assertEqual(mseq.data, [5, 4, 3, 2, 1])

        # clear
        mseq.clear()
        self.assertEqual(mseq.data, [])

    def test_ListStorage(self):
        @plumbing(MutableSequence, ListStorage)
        class ListSequence(object):
            pass

        lseq = ListSequence()
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

    def test_SequenceNode(self):
        @plumbing(SequenceNodeBehavior, ListStorage)
        class SequenceNode(object):
            pass

        root = BaseNode()
        node = root['seq'] = SequenceNode()

        # __name__
        self.assertEqual(node.name, 'seq')

        # __parent__
        self.assertEqual(node.parent, root)

        # path
        self.assertEqual(node.path, [None, 'seq'])

        # root
        self.assertEqual(node.root, root)

        # acquire
        class INoInterface(Interface):
            pass

        self.assertEqual(node.acquire(BaseNode), root)
        self.assertEqual(node.acquire(IMappingNode), root)
        self.assertEqual(node.acquire(INoInterface), None)

        # detach
        child = BaseNode()
        node.insert(0, child)
        self.assertTrue(child in node)
        node.detach('0')
        self.assertFalse(child in node)

        # printtree
        self.checkOutput("""
        <class 'node.base.BaseNode'>: None
          <class 'node.tests.test_sequence.SequenceNode'>: seq
        """, root.treerepr())

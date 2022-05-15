from node.base import BaseNode
from node.behaviors import ListStorage
from node.behaviors import MutableSequence
from node.behaviors import Sequence
from node.behaviors import SequenceNode as SequenceNodeBehavior
from node.interfaces import IContentishNode
from node.interfaces import IMappingNode
from node.interfaces import INode
from node.interfaces import ISequenceNode
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
        self.assertEqual(seq.index(2), 1)
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

    def test_SequenceNode(self):
        @plumbing(SequenceNodeBehavior, ListStorage)
        class SequenceNode(object):
            pass

        root = BaseNode()

        node = root['seq'] = SequenceNode()
        self.assertTrue(INode.providedBy(node))
        self.assertTrue(IContentishNode.providedBy(node))
        self.assertTrue(ISequenceNode.providedBy(node))

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
        child_0 = BaseNode()
        node.insert('0', child_0)
        child_1 = BaseNode()
        node.insert('1', child_1)
        self.assertTrue(child_0 in node)
        node.detach('0')
        self.assertFalse(child_0 in node)
        self.assertEqual(child_0.parent, None)
        self.assertEqual(child_1.name, '0')
        del node[:]

        # __index__
        with self.assertRaises(IndexError):
            node.__index__()
        child_0 = SequenceNode()
        node.insert(0, child_0)
        self.assertEqual(child_0.__index__(), 0)

        # __getitem__
        child_1 = BaseNode()
        node.insert(1, child_1)
        child_2 = BaseNode()
        node.insert(2, child_2)
        self.assertEqual(node[0], child_0)
        self.assertEqual(node['0'], child_0)
        self.assertEqual(node[:2], [child_0, child_1])
        self.assertEqual(node[1:], [child_1, child_2])

        # __setitem__
        node[2] = BaseNode()
        node['2'] = BaseNode()
        self.assertFalse(node[2] is child_2)

        # __delitem__
        child_2 = node['2']
        del node[1]
        self.assertEqual(node[:], [child_0, child_2])

        # insert
        child_1 = BaseNode()
        node.insert(1, child_1)
        self.assertEqual(node[:], [child_0, child_1, child_2])

        # printtree
        self.checkOutput("""
        <class 'node.base.BaseNode'>: None
        __<class 'node.tests.test_sequence.SequenceNode'>: seq
        ____<class 'node.tests.test_sequence.SequenceNode'>: 0
        ____<class 'node.base.BaseNode'>: 1
        ____<class 'node.base.BaseNode'>: 2
        """, root.treerepr(prefix='_'))

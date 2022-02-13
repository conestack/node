from node.behaviors.sequence import ListStorage
from node.behaviors.sequence import MutableSequence
from node.behaviors.sequence import Sequence
from node.tests import NodeTestCase
from plumber import plumbing


class TestSequence(NodeTestCase):

    def test_Sequence(self):
        @plumbing(Sequence)
        class AbstractTestSequence(object):
            pass

        seq = AbstractTestSequence()
        with self.assertRaises(NotImplementedError):
            seq[0]
        with self.assertRaises(NotImplementedError):
            len(seq)

        @plumbing(Sequence)
        class TestSequence(object):
            def __init__(self, data):
                self.data = data

            def __getitem__(self, idx):
                return self.data[idx]

            def __len__(self):
                return len(self.data)

        seq = TestSequence([1, 2, 3])

        # __iter__
        self.assertEqual(list(iter(seq)), [1, 2, 3])

        # __contains__
        self.assertTrue(1 in seq)
        self.assertFalse(4 in seq)

        # __reversed__
        self.assertEqual(list(reversed(seq)), [3, 2, 1])

        # index
        self.assertEquals(seq.index(2), 1)
        with self.assertRaises(ValueError):
            seq.index(4)

        # count
        self.assertEqual(seq.count(1), 1)
        self.assertEqual(seq.count(4), 0)

        # __getitem__
        self.assertEqual(seq[0], 1)
        with self.assertRaises(IndexError):
            seq[3]

        # __len__
        self.assertEqual(len(seq), 3)

from node.behaviors import DictStorage
from node.behaviors import FullMapping
from node.behaviors import ListStorage
from node.behaviors import MappingAdopt
from node.behaviors import MutableSequence
from node.behaviors import SequenceAdopt
from node.interfaces import IMappingAdopt
from node.interfaces import ISequenceAdopt
from node.testing.env import MockupNode
from node.testing.env import NoNode
from node.tests import NodeTestCase
from plumber import plumbing


class TestAdopt(NodeTestCase):

    def test_MappingAdopt(self):
        @plumbing(MappingAdopt, FullMapping, DictStorage)
        class AdoptingDict(object):
            pass

        ad = AdoptingDict()
        self.assertTrue(IMappingAdopt.providedBy(ad))

        # The mockup node is adopted
        node = MockupNode()
        ad['foo'] = node
        self.assertTrue(ad['foo'] is node)
        self.assertEqual(node.__name__, 'foo')
        self.assertTrue(node.__parent__ is ad)

        # The non-node object is not adopted
        nonode = NoNode()
        ad['bar'] = nonode
        self.assertTrue(ad['bar'] is nonode)
        self.assertFalse(hasattr(nonode, '__name__'))
        self.assertFalse(hasattr(nonode, '__parent__'))

        # If something goes wrong, the adoption does not happen.
        # All exceptions are caught.
        class FakeDict(object):
            def __setitem__(self, key, value):
                raise KeyError(key)

            def setdefault(self, key, default=None):
                pass  # pragma: no cover

        @plumbing(MappingAdopt)
        class FailingAD(FakeDict):
            pass

        fail = FailingAD()
        node = MockupNode()

        with self.assertRaises(KeyError):
            fail['foo'] = node

        self.assertEqual(node.__name__, None)
        self.assertEqual(node.__parent__, None)

    def test_SequenceAdopt(self):
        @plumbing(SequenceAdopt, MutableSequence, ListStorage)
        class AdoptingList(object):
            pass

        al = AdoptingList()
        self.assertTrue(ISequenceAdopt.providedBy(al))

        # The mockup node is adopted
        node = MockupNode()
        al.insert(0, node)
        self.assertTrue(al[0] is node)
        self.assertEqual(node.__name__, '0')
        self.assertTrue(node.__parent__ is al)

        al[0] = node = MockupNode()
        self.assertTrue(al[0] is node)
        self.assertEqual(node.__name__, '0')
        self.assertTrue(node.__parent__ is al)

        # The non-node object is not adopted
        nonode = NoNode()
        al[0] = nonode
        self.assertTrue(al[0] is nonode)
        self.assertFalse(hasattr(nonode, '__name__'))
        self.assertFalse(hasattr(nonode, '__parent__'))

        # Slicing is not supported
        with self.assertRaises(NotImplementedError):
            al[:] = [1, 2, 3]

        # If something goes wrong, the adoption does not happen.
        # All exceptions are caught.
        class FakeList(object):
            def __setitem__(self, index, value):
                pass  # pragma: no cover

            def insert(self, index, value):
                raise Exception()

        @plumbing(SequenceAdopt)
        class FailingAL(FakeList):
            pass

        fail = FailingAL()
        node = MockupNode()

        with self.assertRaises(Exception):
            fail.insert(0, node)

        self.assertEqual(node.__name__, None)
        self.assertEqual(node.__parent__, None)

    def test_BC_imports(self):
        from node.behaviors import Adopt
        self.assertTrue(Adopt is MappingAdopt)

        from node.interfaces import IAdopt
        self.assertTrue(IAdopt is IMappingAdopt)

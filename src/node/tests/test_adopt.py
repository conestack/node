from node.behaviors import MappingAdopt
from node.testing.env import MockupNode
from node.testing.env import NoNode
from node.tests import NodeTestCase
from plumber import plumbing


class TestAdopt(NodeTestCase):

    def test_MappingAdopt(self):
        # A dictionary is used as end point
        @plumbing(MappingAdopt)
        class AdoptingDict(dict):
            pass

        ad = AdoptingDict()

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
            def __setitem__(self, key, val):
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

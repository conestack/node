from node.behaviors import Adopt
from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import Fallback
from node.behaviors import NodeChildValidate
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.tests import NodeTestCase
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Nodespaces,
    Fallback,
    Adopt,
    DefaultInit,
    Nodify,
    OdictStorage)
class FallbackNodeAttributes(object):
    """Attributes Node for testing
    """


@plumbing(
    NodeChildValidate,
    Nodespaces,
    Adopt,
    Attributes,
    DefaultInit,
    Nodify,
    OdictStorage)
class FallbackNode(object):
    """Normal Node for testing
    """
    attributes_factory = FallbackNodeAttributes


###############################################################################
# Tests
###############################################################################

class TestFallback(NodeTestCase):

    def setUp(self):
        # Setup test data
        super(TestFallback, self).setUp()

        # Define a root node
        fb_node = self.fb_node = FallbackNode(name='root')

        # It has a fallback subtree defined
        fb_node.fallback_key = 'x'

        # The fallback subtree defines a fallback sub tree for itself.
        # Note that attrs internally is also a tree!
        fb_node['x'] = FallbackNode()
        fb_node['x'].fallback_key = '1'

        # Define node without fallback, but with data
        fb_node['x']['1'] = FallbackNode()

        # An expected fallback value
        fb_node['x']['1'].attrs['a'] = 1

        # An unexpected fallback value. To make them better visible, they are
        # negative in this test
        fb_node['x']['1'].attrs['d'] = -3

        # Same on a second node for a different use case, where it find the
        # value on this level
        fb_node['x']['2'] = FallbackNode()
        fb_node['x']['2'].attrs['b'] = 2
        fb_node['x']['2'].attrs['d'] = -2

        # Define a second subtree
        fb_node['y'] = FallbackNode()

        # Here we have also a subtree which acts as fallback
        fb_node['y'].fallback_key = '1'

        # Again some data-only nodes in the subtree, still a fallback use case
        fb_node['y']['1'] = FallbackNode()
        fb_node['y']['1'].attrs['c'] = 3
        fb_node['y']['1'].attrs['d'] = -1

        # Define the node where our tests will look for the value
        fb_node['y']['2'] = FallbackNode()
        fb_node['y']['2'].attrs['d'] = 4

    def test_test_data(self):
        # Visualize the tree
        self.assertEqual(self.fb_node.treerepr(), (
            '<class \'node.tests.test_fallback.FallbackNode\'>: root\n'
            '  <class \'node.tests.test_fallback.FallbackNode\'>: x\n'
            '    <class \'node.tests.test_fallback.FallbackNode\'>: 1\n'
            '    <class \'node.tests.test_fallback.FallbackNode\'>: 2\n'
            '  <class \'node.tests.test_fallback.FallbackNode\'>: y\n'
            '    <class \'node.tests.test_fallback.FallbackNode\'>: 1\n'
            '    <class \'node.tests.test_fallback.FallbackNode\'>: 2\n'
        ))

    def test_Fallback(self):
        # We always ask for attributes in the path 'root, y, 2, attrs'.
        # 'attrs' is in fact a nodespace '__attributes__', but internally its
        # handled like contained. See nodespaces for more info on it, this is
        # not fallback specific.

        # Case 1 - Directly ask for the key 'd'
        self.assertEqual(self.fb_node['y']['2'].attrs['d'], 4)

        # Case 2 - Ask for a key 'c' which does not exist in path. Now after
        # not finding it there it goes up one level to 'root, y'. Here it looks
        # if there is a fallback defined. There is one, its the subtree
        # 'root, y, 1'. Now it looks there relative in 'attrs' for 'c' and has
        # a hit. Value returned.
        self.assertEqual(self.fb_node['y']['2'].attrs['c'], 3)

        # Case 3 - Ask for a key 'b' which does not exist in the path. Now
        # after not finding it there it goes up one level to 'root, y'. Here it
        # looks if there is a fallback defined. There is one, its the subtree
        # 'root, y, 1'. It looks there relative in attrs for 'b' and it does
        # not exist. After not finding it there it goes up one level to
        # 'root, y'. It has a fallback, but that one was already visited.
        # Now it goes up another level on 'root' and looks if there is a
        # fallback defined. There is one, its the subtree 'root, x'. Now it
        # looks there relative for path '2, attrs, b' and has a hit. Value
        # returned.
        self.assertEqual(self.fb_node['y']['2'].attrs['b'], 2)

        # Case 4 - Ask for a key 'a' which does not exist in the path. Now
        # after not finding it there it goes up one level to 'root, y'. Here
        # it looks if there is a fallback defined. There is one, its the
        # subtree 'root, y, 1'. It looks there relative in attrs for a and it
        # does not exist. After not finding it there it goes up one level to
        # 'root, y'. It has a fallback, but that one was already visited.
        # Now it goes up another level on 'root' and looks if there is a
        # fallback defined. There is one, its the subtree 'root, x'. Now it
        # looks there relative for path '2, attrs, a' and it does not exist.
        # After not finding it there it goes up one level to 'root, x'. Here
        # it looks if there is a fallback defined. There is one, its the
        # subtree 'root, x, 1'. Now it looks there relative for path
        # 'attrs, a' and hit! Return value.
        self.assertEqual(self.fb_node['y']['2'].attrs['a'], 1)

        # Case 5 - When there is no fallback defined. We ask for a key 'z'
        # which does not exist in the path. Now after not finding it there it
        # goes up one level to 'root, y'. Here it looks if there is a fallback
        # defined. There is one, its the subtree 'root, y, 1'. It looks there
        # relative in attrs for z and it does not exist. After not finding it
        # there it goes up one level to 'root, y'. It has a fallback, but that
        # one was already visited. Now it goes up another level on 'root' and
        # looks if there is a fallback defined. There is one, its the subtree
        # 'root, x'. Now it looks there relative for path '2, attrs, z' and it
        # does not exist. After not finding it there it goes up one level to
        # 'root, x'. Here it looks if there is a fallback defined. There is
        # one, its the subtree 'root, x, 1'. Now it looks there relative for
        # path 'attrs, z' and it does not exist. After not finding it there it
        # goes up one level to 'root'. It has a fallback, but that one was
        # already visited. Next parent is None. Exit. No value found. Raise
        # KeyError
        def case_5_raises():
            self.fb_node['y']['2'].attrs['z']
        err = self.expectError(KeyError, case_5_raises)
        self.assertEqual(str(err), '\'z\'')

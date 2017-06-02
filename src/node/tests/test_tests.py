from node.compat import IS_PY2
from node.testing import env
from node.tests import Failure
from node.tests import NodeTestCase
from node.tests import patch
from node.tests import unittest


###############################################################################
# Mock objects
###############################################################################

class PatchedMockupNode(object):
    pass


class PatchedNoNode(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestPatch(unittest.TestCase):

    @patch(env, 'MockupNode', PatchedMockupNode)
    def test_patch(self):
        self.assertEqual(env.MockupNode, PatchedMockupNode)

    @patch(env, 'MockupNode', PatchedMockupNode)
    @patch(env, 'NoNode', PatchedNoNode)
    def test_multi_patch(self):
        self.assertEqual(env.MockupNode, PatchedMockupNode)
        self.assertEqual(env.NoNode, PatchedNoNode)

    def test_patched_raises(self):
        def raises():
            raise Exception()

        @patch(env, 'MockupNode', PatchedMockupNode)
        @patch(env, 'NoNode', PatchedNoNode)
        def test_raises():
            self.assertEqual(env.MockupNode.__name__, 'PatchedMockupNode')
            self.assertEqual(env.NoNode.__name__, 'PatchedNoNode')
            raises()

        self.assertRaises(Exception, test_raises)
        self.assertEqual(env.MockupNode.__name__, 'MockupNode')
        self.assertEqual(env.NoNode.__name__, 'NoNode')


class TestNodeTestCase(NodeTestCase):

    def test_except_error(self):
        def func_raises():
            raise Exception('Function raises')
        err = self.except_error(Exception, func_raises)
        self.assertEqual(str(err), 'Function raises')

        def func_passes():
            pass
        err = None
        try:
            self.except_error(Exception, func_passes)
        except Exception as e:
            err = e
        finally:
            expected = (
                'Expected \'<type \'exceptions.Exception\'>\' when calling'
                ' \'<function func_passes at '
            ) if IS_PY2 else (
                'Expected \'<class \'Exception\'>\' when calling \'<function '
                'TestNodeTestCase.test_except_error.<locals>.func_passes at'
            )
            self.assertTrue(str(err).startswith(expected))

    def test_check_output(self):
        want = '...Hello...'
        got = 'Leading Hello Trailing'
        self.check_output(want, got)
        want = 'Hello'
        err = self.except_error(Failure, self.check_output, want, got)
        self.assertEqual(str(err).split('\n'), [
            'Expected:',
            '    Hello',
            'Got:',
            '    Leading Hello Trailing'
        ])

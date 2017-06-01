from node.compat import IS_PY2
from node.testing import env
import doctest
import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


class patch(object):

    def __init__(self, module, name, ob):
        self.module = module
        self.name = name
        self.ob = ob

    def __call__(self, ob):
        wrap = False
        if not hasattr(ob, '__test_patches__'):
            ob.__test_patches__ = list()
            wrap = True
        ob.__test_patches__.append((self.module, self.name, self.ob))
        if wrap:
            def _wrapped(*args, **kw):
                orgin = list()
                for module, name, obj in ob.__test_patches__:
                    orgin.append((module, name, getattr(module, name)))
                    setattr(module, name, obj)
                try:
                    ob(*args, **kw)
                except Exception as e:
                    raise e
                finally:
                    for module, name, obj in orgin:
                        setattr(module, name, obj)
            return _wrapped
        return ob


class PatchedMockupNode(object):
    pass


class PatchedNoNode(object):
    pass


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

        @patch(env, 'NoNode', PatchedNoNode)
        def test_raises():
            self.assertEqual(env.NoNode.__name__, 'PatchedNoNode')
            raises()

        self.assertRaises(Exception, test_raises)
        self.assertEqual(env.NoNode.__name__, 'NoNode')


class Example(object):

    def __init__(self, want):
        self.want = want + '\n'


class Failure(Exception):
    pass


class NodeTestCase(unittest.TestCase):

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self._checker = doctest.OutputChecker()
        self._optionflags = (
            doctest.NORMALIZE_WHITESPACE |
            doctest.ELLIPSIS |
            doctest.REPORT_ONLY_FIRST_FAILURE
        )

    def except_error(self, exc, func, *args, **kw):
        try:
            func(*args, **kw)
        except exc as e:
            return e
        else:
            msg = 'Expected \'{}\' when calling \'{}\''.format(exc, func)
            raise Exception(msg)

    def check_output(self, want, got, optionflags=None):
        if optionflags is None:
            optionflags = self._optionflags
        success = self._checker.check_output(want, got, optionflags)
        if not success:
            raise Failure(self._checker.output_difference(
                Example(want),
                got, optionflags
            ))


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


def test_suite():
    from node.tests import test_base
    from node.tests import test_locking
    from node.tests import test_serializer
    from node.tests import test_testing_base
    from node.tests import test_testing_env
    from node.tests import test_testing_fullmapping
    from node.tests import test_utils

    suite = unittest.TestSuite()

    suite.addTest(TestPatch('test_patch'))
    suite.addTest(TestPatch('test_multi_patch'))
    suite.addTest(TestPatch('test_patched_raises'))
    suite.addTest(TestNodeTestCase('test_except_error'))
    suite.addTest(TestNodeTestCase('test_check_output'))

    suite.addTest(unittest.findTestCases(test_testing_env))
    suite.addTest(unittest.findTestCases(test_testing_base))
    suite.addTest(unittest.findTestCases(test_testing_fullmapping))

    suite.addTest(unittest.findTestCases(test_base))
    suite.addTest(unittest.findTestCases(test_utils))
    suite.addTest(unittest.findTestCases(test_locking))
    suite.addTest(unittest.findTestCases(test_serializer))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(test_suite())

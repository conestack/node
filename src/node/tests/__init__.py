import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


IS_PY2 = sys.version_info[0] < 3
IS_PYPY = '__pypy__' in sys.builtin_module_names
ITER_FUNC = 'iteritems' if IS_PY2 else 'items'


class NodeTestCase(unittest.TestCase):

    def except_error(self, exc, func, *args, **kw):
        try:
            func(*args, **kw)
        except exc as e:
            return e
        else:
            msg = 'Expected \'{}\' when calling \'{}\''.format(exc, func)
            raise Exception(msg)

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
                'NodeTestCase.test_except_error.<locals>.func_passes at'
            )
            self.assertTrue(str(err).startswith(expected))


def test_suite():
    from node.tests import test_base
    from node.tests import test_testing_env
    from node.tests import test_testing_base
    from node.tests import test_testing_fullmapping
    from node.tests import test_utils

    suite = unittest.TestSuite()
    suite.addTest(unittest.findTestCases(test_testing_env))
    suite.addTest(unittest.findTestCases(test_testing_base))
    suite.addTest(unittest.findTestCases(test_testing_fullmapping))

    suite.addTest(unittest.findTestCases(test_utils))

    #suite.addTest(unittest.findTestCases(test_base))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(test_suite())

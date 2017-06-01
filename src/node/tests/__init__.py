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


def test_suite():
    from node.tests import test_base
    from node.tests import test_locking
    from node.tests import test_serializer
    from node.tests import test_testing
    from node.tests import test_tests
    from node.tests import test_utils

    suite = unittest.TestSuite()
    suite.addTest(unittest.findTestCases(test_tests))
    suite.addTest(unittest.findTestCases(test_testing))
    suite.addTest(unittest.findTestCases(test_base))
    suite.addTest(unittest.findTestCases(test_utils))
    suite.addTest(unittest.findTestCases(test_locking))
    suite.addTest(unittest.findTestCases(test_serializer))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(test_suite())

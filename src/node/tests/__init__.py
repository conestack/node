import doctest
import sys
import unittest


class patch(object):

    def __init__(self, module, name, ob):
        self.module = module
        self.name = name
        self.ob = ob

    def __call__(self, ob):
        ob.__test_patch__ = (self.module, self.name, self.ob)

        def _wrapped(*args, **kw):
            module, name, obj = ob.__test_patch__
            orgin = (module, name, getattr(module, name))
            setattr(module, name, obj)
            try:
                ob(*args, **kw)
            except Exception as e:
                raise e
            finally:
                module, name, obj = orgin
                setattr(module, name, obj)
        return _wrapped


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

    def expect_error(self, exc, func, *args, **kw):
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
    from node.tests import test_alias
    from node.tests import test_attributes
    from node.tests import test_base
    from node.tests import test_cache
    from node.tests import test_common
    from node.tests import test_events
    from node.tests import test_fallback
    from node.tests import test_lifecycle
    from node.tests import test_locking
    from node.tests import test_mapping
    from node.tests import test_nodespace
    from node.tests import test_nodify
    from node.tests import test_order
    from node.tests import test_reference
    from node.tests import test_serializer
    from node.tests import test_storage
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
    suite.addTest(unittest.findTestCases(test_events))

    suite.addTest(unittest.findTestCases(test_alias))
    suite.addTest(unittest.findTestCases(test_attributes))
    suite.addTest(unittest.findTestCases(test_cache))
    suite.addTest(unittest.findTestCases(test_common))
    suite.addTest(unittest.findTestCases(test_fallback))
    suite.addTest(unittest.findTestCases(test_lifecycle))
    suite.addTest(unittest.findTestCases(test_mapping))
    suite.addTest(unittest.findTestCases(test_nodespace))
    suite.addTest(unittest.findTestCases(test_nodify))
    suite.addTest(unittest.findTestCases(test_order))
    suite.addTest(unittest.findTestCases(test_reference))
    suite.addTest(unittest.findTestCases(test_storage))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(test_suite())

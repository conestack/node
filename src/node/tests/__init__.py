import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


def test_suite():
    from node.tests import test_testing_env
    from node.tests import test_testing_base
    from node.tests import test_testing_fullmapping

    suite = unittest.TestSuite()
    suite.addTest(unittest.findTestCases(test_testing_env))
    suite.addTest(unittest.findTestCases(test_testing_base))
    suite.addTest(unittest.findTestCases(test_testing_fullmapping))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(test_suite())

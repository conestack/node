from node.testing.base import BaseTester
from node.testing.base import ContractError
from odict import odict
import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


class TestBase(unittest.TestCase):

    def test_BaseTester(self):
        # BaseTester is used to write testing code for an interface contract.
        # A subclass must define ``iface_contract`` containing the functions
        # names of interface to be tested and a testing function for each
        # contract function prefixed with 'test_'
        class DummyTester(BaseTester):
            iface_contract = ['func_a', 'func_b', 'func_c']

            def test_func_a(self):
                self.context.func_a()

            def test_func_b(self):
                self.context.func_b()

            def test_func_c(self):
                self.context.func_c()

        # Test implementations
        class FuncAImpl(object):

            def func_a(self):
                pass

        class FuncBImpl(FuncAImpl):

            def func_b(self):
                raise Exception('func_b failed')

        # Tester object expects the implementation class on init, and optional
        # a already instantiated testing instance. If context is not given,
        # it is instantiated by given class without arguments
        tester = DummyTester(FuncBImpl)

        # Run and print combined results
        tester.run()
        self.assertEqual(tester.combined.split('\n'), [
            '``func_a``: OK',
            '``func_b``: failed: Exception(\'func_b failed\',)',
            '``func_c``: failed: AttributeError("\'FuncBImpl\' object has no '
            'attribute \'func_c\'",)'
        ])

        # Get results of testing as odict
        res = odict([
            ('func_a', 'OK'),
            ('func_b', 'failed: Exception(\'func_b failed\',)'),
            ('func_c', 'failed: AttributeError("\'FuncBImpl\' object has no '
                       'attribute \'func_c\'",)')
        ])
        self.assertEqual(tester.results, res)

        # Print classes which actually provides the function implementation
        self.assertEqual(tester.wherefrom.split('\n'), [
            'func_a: FuncAImpl',
            'func_b: FuncBImpl',
            'func_c: function not found on object'
        ])

        # A tester can be forced to raise exceptions directly instead of
        # collecting them
        tester.direct_error = True
        err = None
        try:
            tester.run()
        except Exception as e:
            err = e
        finally:
            self.assertEqual(str(err), 'func_b failed')

        # If tester does define a function to test in ``iface_contract`` but
        # not implements the related testing function, ``run`` will fail
        class BrokenTester(BaseTester):
            iface_contract = ['test_me']

        err = None
        try:
            tester = BrokenTester(FuncBImpl)
            tester.run()
        except ContractError as e:
            err = e
        finally:
            self.assertEqual(
                str(err),
                '``BrokenTester`` does not provide ``test_test_me``'
            )


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover

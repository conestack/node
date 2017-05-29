import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


class TestBase(unittest.TestCase):

    def test_foo(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover

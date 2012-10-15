import unittest
import doctest
from pprint import pprint
from interlude import interact

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'testing/env.rst',
    'testing/base.rst',
    'testing/fullmapping.rst',
    'base.rst',
    'utils.rst',
    'locking.rst',
    'behaviors/alias.rst',
    'behaviors/attributes.rst',
    'behaviors/cache.rst',
    'behaviors/lifecycle.rst',
    'behaviors/mapping.rst',
    'behaviors/nodespace.rst',
    'behaviors/nodify.rst',
    'behaviors/order.rst',
    'behaviors/reference.rst',
    'behaviors/storage.rst',
    '../../README.rst',
    # at very end, ``GetattrChildren`` tests break coverage recording
    'behaviors/common.rst',
]


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for file in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE

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
    'aliasing.rst',
    'locking.rst',
    'parts/alias.rst',
    'parts/attributes.rst',
    'parts/cache.rst',
    'parts/lifecycle.rst',
    'parts/mapping.rst',
    'parts/nodespace.rst',
    'parts/nodify.rst',
    'parts/order.rst',
    'parts/reference.rst',
    'parts/storage.rst',
    'bbb.rst',
    '../../README.rst',
    # at very end, ``GetattrChildren`` tests break coverage recording
    'parts/common.rst',
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
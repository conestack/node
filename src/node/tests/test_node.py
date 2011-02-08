import unittest
import doctest 
from pprint import pprint
from interlude import interact

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'env.txt',
    '../testing/fullmapping.txt',
    '../testing/location.txt',
    '../testing/node.txt',
    '../base.txt',
    '../utils.txt',
    '../aliasing.txt',
    '../locking.txt',
    '../parts/alias.txt',
    '../parts/attributes.txt',
    '../parts/cache.txt',
    '../parts/common.txt',
    '../parts/lifecycle.txt',
    '../parts/mapping.txt',
    '../parts/nodespace.txt',
    '../parts/nodify.txt',
    '../parts/order.txt',
    '../parts/reference.txt',
    '../original.txt',
    '../../../README.rst',
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
    unittest.main(defaultTest='test_suite')

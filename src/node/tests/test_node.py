import unittest
import doctest 
from pprint import pprint
from interlude import interact

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'env.txt',
    '../testing/base.txt',
    '../testing/fullmapping.txt',
    '../base.txt',
    '../utils.txt',
    '../aliasing.txt',
    '../locking.txt',
    '../parts/alias.txt',
    '../parts/attributes.txt',
    '../parts/cache.txt',
    
    # something happens in this test breaking coverage recording, moved test 
    # to the end
    #'../parts/common.txt', 
    
    '../parts/lifecycle.txt',
    '../parts/mapping.txt',
    '../parts/nodespace.txt',
    '../parts/nodify.txt',
    '../parts/order.txt',
    '../parts/reference.txt',
    '../parts/storage.txt',
    '../bbb.txt',
    '../../../README.rst',
    
    # tmp at end, figure out what makes coverage break recording
    '../parts/common.txt',
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

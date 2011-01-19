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
    
    '../plumbing/adopt.txt',
    #'../plumbing/validate.txt',
    '../plumbing/alias.txt',
    '../plumbing/attributes.txt',
    '../plumbing/nodespace.txt',
    #'../plumbing/order.txt',
    #'../plumbing/reference.txt',
    '../plumbing/unicode.txt',
    '../plumbing/wrap.txt',
    
    #'../../../README.rst',
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

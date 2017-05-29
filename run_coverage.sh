#!/bin/sh
if [ -x "$(which python)" ]; then
    ./py2/bin/coverage run -m node.tests.test_suite
    ./py2/bin/coverage report
fi
if [ -x "$(which python3)" ]; then
    ./py3/bin/coverage run -m node.tests.test_suite
    ./py3/bin/coverage report
fi
if [ -x "$(which pypy)" ]; then
    ./pypy/bin/coverage run -m node.tests.test_suite
    ./pypy/bin/coverage report
fi

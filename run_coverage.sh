#!/bin/sh
if [ -x "$(which python)" ]; then
    ./py2/bin/coverage run -m node.tests.__init__
    ./py2/bin/coverage report
fi
if [ -x "$(which python3)" ]; then
    ./py3/bin/coverage run -m node.tests.__init__
    ./py3/bin/coverage report
fi
if [ -x "$(which pypy)" ]; then
    ./pypy/bin/coverage run -m node.tests.__init__
    ./pypy/bin/coverage report
fi

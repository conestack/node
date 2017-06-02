#!/bin/bash

if [ -x "$(which python)" ]; then
    rm -r py2

    virtualenv --clear --no-site-packages -p python py2

    ./py2/bin/pip install coverage
    ./py2/bin/pip install zope.interface
    ./py2/bin/pip install zope.lifecycleevent
    ./py2/bin/pip install zope.component
    ./py2/bin/pip install zope.deprecation

    pushd devsrc/odict
    ../../py2/bin/python setup.py develop
    popd

    pushd devsrc/plumber
    ../../py2/bin/python setup.py develop
    popd

    ./py2/bin/python setup.py develop
fi
if [ -x "$(which python3)" ]; then
    rm -r py3

    virtualenv --clear --no-site-packages -p python3 py3

    ./py3/bin/pip install coverage
    ./py3/bin/pip install zope.interface
    ./py3/bin/pip install zope.lifecycleevent
    ./py3/bin/pip install zope.component
    ./py3/bin/pip install zope.deprecation

    pushd devsrc/odict
    ../../py3/bin/python setup.py develop
    popd

    pushd devsrc/plumber
    ../../py3/bin/python setup.py develop
    popd

    ./py3/bin/python setup.py develop
fi
if [ -x "$(which pypy)" ]; then
    rm -r pypy

    virtualenv --clear --no-site-packages -p pypy pypy

    ./pypy/bin/pip install coverage
    ./pypy/bin/pip install zope.interface
    ./pypy/bin/pip install zope.lifecycleevent
    ./pypy/bin/pip install zope.component
    ./pypy/bin/pip install zope.deprecation

    pushd devsrc/odict
    ../../pypy/bin/python setup.py develop
    popd

    pushd devsrc/plumber
    ../../pypy/bin/python setup.py develop
    popd

    ./pypy/bin/python setup.py develop
fi

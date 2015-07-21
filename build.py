"""Building the package:

Look into pyc::

    git clone https://github.com/gstarnberger/uncompyle.git
    cd uncompyle/
    sudo ./setup.py install
    uncompyler.py pyc_file_to_decompile.pyc > recovered_file.py

Building sdist::

    python build.py clean
    python build.py sdist

Build bdist_egg::

    python setup.py bdist_egg --exclude-source-files
"""


from setuptools import find_packages
from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import os
import subprocess
import sys


extensions = [
    Extension('node.base', ['src/node/base.py']),
    Extension('node.events', ['src/node/events.py']),
    Extension('node.locking', ['src/node/locking.py']),
    Extension('node.parts', ['src/node/parts.py']),
    # test fails right now
    # Extension('node.utils', ['src/node/utils.py']),
    Extension('node.behaviors.alias', ['src/node/behaviors/alias.py']),
    Extension('node.behaviors.attributes', ['src/node/behaviors/attributes.py']),
    Extension('node.behaviors.cache', ['src/node/behaviors/cache.py']),
    Extension('node.behaviors.common', ['src/node/behaviors/common.py']),
    Extension('node.behaviors.lifecycle', ['src/node/behaviors/lifecycle.py']),
    Extension('node.behaviors.mapping', ['src/node/behaviors/mapping.py']),
    Extension('node.behaviors.nodespace', ['src/node/behaviors/nodespace.py']),
    Extension('node.behaviors.nodify', ['src/node/behaviors/nodify.py']),
    Extension('node.behaviors.order', ['src/node/behaviors/order.py']),
    Extension('node.behaviors.reference', ['src/node/behaviors/reference.py']),
    Extension('node.behaviors.storage', ['src/node/behaviors/storage.py']),
]


args = sys.argv[1:]
if 'clean' in args:
    print 'Delete build'
    subprocess.Popen(
        'rm -rf build',
        shell=True,
        executable='/bin/bash'
    )
    print 'Delete C files'
    subprocess.Popen(
        'find . -name "*.c" | xargs rm',
        shell=True,
        executable='/bin/bash'
    )
    print 'Delete SO files'
    subprocess.Popen(
        'find . -name "*.so" | xargs rm',
        shell=True,
        executable='/bin/bash'
    )


setup(
    name='node',
    #packages=find_packages('src'),
    #package_dir={'': 'src'},
    #namespace_packages=['node'],
    #include_package_data=True,
    #zip_safe=True,
    #install_requires=[
    #    'setuptools',
    #    'odict>=1.5.1',
    #    'plumber>=1.3',
    #    'zope.lifecycleevent',
    #    'zope.deprecation',
    #    'zope.component',
    #],
    #extras_require={
    #    'py24': [
    #        'uuid',
    #    ],
    #    'test': [
    #        'interlude',
    #        'plone.testing',
    #        'unittest2',
    #        'odict[test]',
    #        'plumber[test]',
    #    ]
    #},
    ext_modules=cythonize(extensions),
    #entry_points="""
    #"""
    )

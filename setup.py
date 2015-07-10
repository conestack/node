from setuptools import find_packages
from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import os
import subprocess
import sys


version = '0.9.16.dev0'
shortdesc = "Building data structures as node trees"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'CHANGES.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


extensions = [
    Extension('node.base', ['src/node/base.py']),
    Extension('node.events', ['src/node/events.py']),
    # zope.interface -> cythonize fails
    # Extension('node.interfaces', ['src/node/interfaces.py']),
    Extension('node.locking', ['src/node/locking.py']),
    Extension('node.parts', ['src/node/parts.py']),
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
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='',
    author='BlueDynamics Alliance',
    author_email='dev@bluedynamics.com',
    url='http://github.com/bluedynamics/node',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['node'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'odict>=1.5.1',
        'plumber>=1.3',
        'zope.lifecycleevent',
        'zope.deprecation',
        'zope.component',
    ],
    extras_require={
        'py24': [
            'uuid',
        ],
        'test': [
            'interlude',
            'plone.testing',
            'unittest2',
            'odict[test]',
            'plumber[test]',
        ]
    },
    ext_modules=cythonize(extensions),
    entry_points="""
    """)

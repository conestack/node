from setuptools import find_packages
from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import os


version = '0.9.16.dev0'
shortdesc = "Building data structures as node trees"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'CHANGES.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


extensions = [
    Extension('node', [
        'src/node/base.py',
        'src/node/events.py',
        'src/node/interfaces.py',
        'src/node/locking.py',
        'src/node/parts.py',
        'src/node/utils.py',
    ]),
    Extension('node.behaviors', [
        'src/node/behaviors/__init__.py',
        'src/node/behaviors/alias.py',
        'src/node/behaviors/attributes.py',
        'src/node/behaviors/cache.py',
        'src/node/behaviors/common.py',
        'src/node/behaviors/lifecycle.py',
        'src/node/behaviors/mapping.py',
        'src/node/behaviors/nodespace.py',
        'src/node/behaviors/nodify.py',
        'src/node/behaviors/order.py',
        'src/node/behaviors/reference.py',
        'src/node/behaviors/storage.py',
    ])
]


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

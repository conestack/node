# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '0.9.21'
shortdesc = "Building data structures as node trees"
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='node tree fullmapping',
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
            'plone.testing',
            'odict',
            'plumber[test]',
        ]
    },
    test_suite='node.tests.test_suite',
    entry_points="""
    """
)

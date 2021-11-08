# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '0.9.28'
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
    keywords='node tree fullmapping dict',
    author='Node Contributors',
    author_email='dev@conestack.org',
    url='http://github.com/conestack/node',
    license='Simplified BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['node'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'odict>=1.7.0',
        'plumber>1.4.99',
        'zope.lifecycleevent',
        'zope.deprecation',
        'zope.component',
    ],
    test_suite='node.tests.test_suite'
)

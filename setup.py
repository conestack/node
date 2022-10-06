from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '1.1'
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
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
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
        'odict>=1.9.0',
        'plumber>=1.5',
        'setuptools',
        'zope.component',
        'zope.deferredimport',
        'zope.deprecation',
        'zope.lifecycleevent'
    ],
    test_suite='node.tests.test_suite'
)

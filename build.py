"""
Building sdist::

    python build.py clean
    python build.py build_ext --inplace

Create binary distribution egg::

    python setup.py bdist_egg --exclude-source-files

    pip install dist/node-0.9.16.dev0-py2-none-any.whl
"""


# never sort this imports
from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension as Ext
import subprocess
import sys


extensions = [
    Ext('node.base', ['src/node/base.py']),
    Ext('node.events', ['src/node/events.py']),
    Ext('node.locking', ['src/node/locking.py']),
    Ext('node.parts', ['src/node/parts.py']),
    # test fails right now
    # Ext('node.utils', ['src/node/utils.py']),
    Ext('node.behaviors.alias', ['src/node/behaviors/alias.py']),
    Ext('node.behaviors.attributes', ['src/node/behaviors/attributes.py']),
    Ext('node.behaviors.cache', ['src/node/behaviors/cache.py']),
    Ext('node.behaviors.common', ['src/node/behaviors/common.py']),
    Ext('node.behaviors.lifecycle', ['src/node/behaviors/lifecycle.py']),
    Ext('node.behaviors.mapping', ['src/node/behaviors/mapping.py']),
    Ext('node.behaviors.nodespace', ['src/node/behaviors/nodespace.py']),
    Ext('node.behaviors.nodify', ['src/node/behaviors/nodify.py']),
    Ext('node.behaviors.order', ['src/node/behaviors/order.py']),
    Ext('node.behaviors.reference', ['src/node/behaviors/reference.py']),
    Ext('node.behaviors.storage', ['src/node/behaviors/storage.py']),
]


def remove_files_by_extension(ext):
    print 'Delete {0} files'.format(ext)
    subprocess.Popen(
        'find ./src -name "*.{0}" | xargs rm'.format(ext),
        shell=True,
        executable='/bin/bash'
    )


args = sys.argv[1:]
if 'clean' in args:
    print 'Clean build'
    subprocess.Popen('rm -rf build', shell=True, executable='/bin/bash')
    remove_files_by_extension('pyc')
    remove_files_by_extension('c')
    remove_files_by_extension('so')
    sys.exit(0)


setup(
    name='node',
    package_dir={'': 'src'},
    ext_modules=cythonize(extensions))

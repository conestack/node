from setuptools import setup, find_packages
import sys, os

version = '0.1'
shortdesc = "The node"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='node',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://github.com/bluedynamics/node',
      license='General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['node'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'zope.location',
      ],
      extras_require={
          'test': [
              'interlude',
              'plone.testing',
              'unittest2',
          ]
      },
      entry_points="""
      [console_scripts]
      """,
      )

from setuptools import setup, find_packages
import os

version = '0.9'
shortdesc = "The node"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='node',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://github.com/bluedynamics/node',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['node'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'odict',
          'plumber',
          'zope.lifecycleevent',
          'zope.deprecation', # can be removed soon
      ],
      extras_require={
          'py24': [
              'uuid',
          ],
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

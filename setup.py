# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

__version__ = u'1.0.0-alpha'
here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, u'README.md'), encoding=u'utf-8') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-iiif',
    version=__version__,
    description=u'A IIIF extenstion for CKAN',
    long_description=__long_description__,
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-iiif',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    license=u'GNU GPLv3',
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'License :: OSI Approved :: GNU General Public License v3 (GNU GPLv3)',
        u'Programming Language :: Python :: 2.7',
    ],
    keywords=u'CKAN IIIF',
    packages=find_packages(exclude=[u'contrib', u'docs', u'tests*']),
    namespace_packages=[u'ckanext'],
    install_requires=[
        u'six~=1.11.0',
    ],
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    package_data={
    },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points=u'''
        [ckan.plugins]
        iiif=ckanext.iiif.plugin:IIIFPlugin
    '''
)

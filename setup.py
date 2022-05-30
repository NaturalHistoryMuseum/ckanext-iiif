# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

__version__ = '2.1.0'
here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    __long_description__ = f.read()

setup(
    name='ckanext-iiif',
    version=__version__,
    description='A IIIF extenstion for CKAN',
    long_description=__long_description__,
    url='https://github.com/NaturalHistoryMuseum/ckanext-iiif',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GNU GPLv3)',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='CKAN IIIF',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanext', 'ckanext.iiif'],
    install_requires=[],
    include_package_data=True,
    package_data={
    },
    data_files=[],
    entry_points='''
        [ckan.plugins]
        iiif=ckanext.iiif.plugin:IIIFPlugin
    '''
)

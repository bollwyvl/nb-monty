#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

with open('nbmonty/version.py') as version:
    exec(version.read())

with open('README.md') as f:
    readme = f.read()

setup(
    name='nb-monty',
    version=__version__,
    description='Semantic cards for the IPython/Jupyter notebook',
    long_description=readme,
    author='Nicholas Bollweg',
    author_email='nick.bollweg@gmail.com',
    url='https://github.com/bollwyvl/nb-monty',
    packages=find_packages(exclude=('tests', 'notebooks')),
    include_package_data=True,
    install_requires=[
        'IPython',
        'rdflib',
        'pyld'
    ],
    classifiers = [
        'Framework :: IPython',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2'
    ],
    test_suite='nose.collector',
)

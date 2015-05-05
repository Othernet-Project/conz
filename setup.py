#!/usr/bin/env python

import os
import sys
from setuptools import setup

SCRIPTDIR = os.path.dirname(__file__) or '.'
PY3 = sys.version_info >= (3, 0, 0)

import conz


def read(fname):
    """ Return content of specified file """
    path = os.path.join(SCRIPTDIR, fname)
    if PY3:
        f = open(path, 'r', encoding='utf8')
    else:
        f = open(path, 'r')
    content = f.read()
    f.close()
    return content


setup(
    name='conz',
    version=conz.__version__,
    author='Outernet Inc',
    author_email='apps@outernet.is',
    description='Library for writing command line programs',
    license='GPLv3',
    keywords='console, terminal, signals, output, command line, colorizing',
    url='https://github.com/Outernet-Project/conz',
    long_description=read('README.rst'),
    py_modules=['conz'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],
)

#!/usr/bin/env python
"""vCard Module setup"""

from setuptools import setup

setup(
    name='vCard-module',
    version='0.6',
    description='vCard validator, class and utility functions',
    author='Victor Engmark',
    author_email='victor.engmark@gmail.com',
    url='http://vcard-module.sourceforge.net/',
    py_modules=['vcard'],
    install_requires = ['isodate'],
    test_suite = 'tests.vcard_test',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Text Processing',
        'Topic :: Utilities',])

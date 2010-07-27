#!/usr/bin/env python
"""Setup configuration"""

from setuptools import find_packages, setup
from vcard.vcard import __doc__ as module_doc

setup(
    name = 'vCard-module',
    version = '0.7.4',
    description = 'vCard validator, class and utility functions',
    long_description = module_doc,
    url = 'http://vcard-module.sourceforge.net/',
    keywords = 'vCard vCards RFC 2426 RFC2426 validator',
    packages = find_packages(exclude=['tests']),
    install_requires = ['isodate'],
    entry_points = {'console_scripts': ['vcard = vcard.vcard:main']},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    test_suite = 'tests.tests',
    author = 'Victor Engmark',
    author_email = 'victor.engmark@gmail.com',
    maintainer = 'Victor Engmark',
    maintainer_email = 'victor.engmark@gmail.com',
    download_url = 'http://sourceforge.net/projects/vcard-module/files/',
    platforms = ['POSIX', 'Windows'],
    license = 'GPL v3 or newer',
    )

#!/usr/bin/env python
"""Setup configuration"""

from setuptools import find_packages, setup
from vcard import vcard as package

setup(
    name = package.__package__,
    version = package.__version__,
    description = 'vCard validator, class and utility functions',
    long_description = package.__doc__,
    url = package.__url__,
    keywords = 'vCard vCards RFC 2426 RFC2426 validator',
    packages = [package.__package__],
    install_requires = ['isodate'],
    entry_points = {
        'console_scripts': [
            '%(package)s = %(package)s.%(package)s:main' % {
                'package': package.__package__}]},
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
    test_suite = 'test.test_package',
    author = package.__author__,
    author_email = package.__email__,
    maintainer = package.__maintainer__,
    maintainer_email = package.__email__,
    download_url = 'http://pypi.python.org/pypi/vcard-module/',
    platforms = ['POSIX', 'Windows'],
    license = package.__license__,
    )

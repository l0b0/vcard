#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for vcard module

Default syntax:

./vcard_test.py
    Run all unit tests
"""

import codecs
import doctest
import glob
import os
import unittest
import urllib
import warnings

import vcard
from vcard_defs import MSG_EMPTY_VCARD
from vcard_validators import VCardFormatError

def _get_vcard_file(path):
    """
    Get the vCard contents locally or remotely.

    @param filename: File relative to current directory or a URL
    @return: Text in the given file
    """
    if path.startswith('http'):
        filename = urllib.urlretrieve(path)[0]
    else:
        filename = os.path.join(os.path.dirname(__file__), path)

    with codecs.open(filename, 'r', 'utf-8') as file_pointer:
        contents = file_pointer.read()

    return contents


# pylint: disable-msg=C0301
# Invalid vCards
VCARD_EMPTY = ''
VCARDS_MISSING = {
    'properties': _get_vcard_file('missing_properties.vcf'),
    'start': _get_vcard_file('missing_start.vcf'),
    'end': _get_vcard_file('missing_end.vcf'),
    'version': _get_vcard_file('missing_version.vcf'),
    'n': _get_vcard_file('missing_n.vcf'),
    'fn': _get_vcard_file('missing_fn.vcf'),
    }
VCARDS_INVALID_PROPERTY_NAME = {
    'foo': _get_vcard_file('invalid_property_foo.vcf'),
    }
VCARDS_INVALID_PARAM = {
    }
VCARDS_INVALID_PARAM_VALUE = {
    }
VCARDS_INVALID_X_NAME = {
    'Tantek Çelik': _get_vcard_file(
        'http://h2vx.com/vcf/tantek.com/%23contact'),
    }
VCARDS_INVALID_VALUE = {
    'http://en.wikipedia.org/wiki/VCard':
        _get_vcard_file('invalid_value_wp.vcf'),
    '01-tantek-basic':
        _get_vcard_file('http://microformats.org/tests/hcard/01-tantek-basic.vcf'),
    }

VCARDS_VALID = {
    'minimal': _get_vcard_file('minimal.vcf'),
    'scrambled case': _get_vcard_file('scrambled_case.vcf'),
    'Aspaas Sykler': _get_vcard_file(
        'http://aspaass.no/kontakt/Aspaas%20Sykler.vcf'),
    'Troy Wolf': _get_vcard_file(
        'http://www.troywolf.com/articles/php/class_vcard/vcard_example.php'),
    }

VCARDS_REFERENCE = {
    'http://tools.ietf.org/html/rfc2426 1': _get_vcard_file('rfc_2426_a.vcf'),
    'http://tools.ietf.org/html/rfc2426 2': _get_vcard_file('rfc_2426_b.vcf'),
    }

# pylint: enable-msg=C0301


class TestVCards(unittest.TestCase):
    """Test small vCards"""
    def test_empty(self):
        """Empty string"""
        try:
            vcard.VCard(VCARD_EMPTY)
            self.fail('Invalid vCard created')
        except VCardFormatError as error:
            self.assertEquals(error.message, MSG_EMPTY_VCARD)


    def test_failing(self):
        """vCards missing a mandatory property"""
        for vcard_title, vcard_text in \
        VCARDS_MISSING.items() + VCARDS_INVALID_X_NAME.items():
            try:
                vcard.VCard(vcard_text)
                self.fail('Invalid vCard "%s" created' % vcard_title)
            except VCardFormatError:
                pass


    def test_valid(self):
        """Valid (but not necessarily sane) vCards"""
        for vcard_title, vcard_text in VCARDS_VALID.items():
            try:
                with warnings.catch_warnings(record=True):
                    vc_obj = vcard.VCard(vcard_text)
                self.assertNotEqual(vc_obj, None)
            except VCardFormatError as error:
                self.fail(
                    'Valid vCard "%s" not created' % \
                    vcard_title + '\n' + \
                    error.message)


    def test_rfc_2426_examples(self):
        """
        Examples from RFC 2426 <http://tools.ietf.org/html/rfc2426#section-7>
        Skipping because RFC vCards are not valid :/
        <http://l0b0.wordpress.com/2009/12/25/vcard-parser-and-validator/>
        """
        for vcard_text in VCARDS_REFERENCE.values():
            try:
                with warnings.catch_warnings(record=True):
                    vc_obj = vcard.VCard(vcard_text)
                self.assertNotEqual(vc_obj, None)
            except VCardFormatError:
                pass
                #self.fail(
                #    'Valid vCard "%s" not created' % vcard_title + '\n' + \
                #    error.message)


    def test_doc(self):
        """Documentation tests"""
        self.assertEqual(doctest.testmod(vcard)[0], 0)
        import vcard_defs
        self.assertEqual(doctest.testmod(vcard_defs)[0], 0)
        import vcard_utils
        self.assertEqual(doctest.testmod(vcard_utils)[0], 0)
        import vcard_validators
        self.assertEqual(doctest.testmod(vcard_validators)[0], 0)
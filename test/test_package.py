#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for vcard <https://github.com/l0b0/vcard>"""

__author__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__copyright__ = 'Copyright (C) 2010-2012 Victor Engmark'
__license__ = 'GPLv3'

import codecs
import doctest
import os
import unittest
import urllib
import warnings

from vcard import vcard
from vcard import vcard_defs
from vcard import vcard_utils
from vcard import vcard_validators

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


# vCards with errors
VCARDS_CONTINUATION_AT_START = {
    'message': vcard_defs.MSG_CONTINUATION_AT_START,
    'vcards': [
        _get_vcard_file('continuation_at_start.vcf')]}
VCARDS_DOT_AT_LINE_START = {
    'message': vcard_defs.MSG_DOT_AT_LINE_START,
    'vcards': [
        _get_vcard_file('dot_at_line_start.vcf')]}
VCARDS_EMPTY_VCARD = {
    'message': vcard_defs.MSG_EMPTY_VCARD,
    'vcards': [
        '',
        None]}
VCARDS_INVALID_DATE = {
    'message': vcard_defs.MSG_INVALID_DATE,
    'vcards': [
        ]}
VCARDS_INVALID_LANGUAGE_VALUE = {
    'message': vcard_defs.MSG_INVALID_LANGUAGE_VALUE,
    'vcards': [
        _get_vcard_file('invalid_language_value.vcf')]}
VCARDS_INVALID_LINE_SEPARATOR = {
    'message': vcard_defs.MSG_INVALID_LINE_SEPARATOR,
    'vcards': [
        _get_vcard_file('line_ending_mac.vcf'),
        _get_vcard_file('line_ending_unix.vcf'),
        _get_vcard_file('line_ending_mixed.vcf')]}
VCARDS_INVALID_PARAM_NAME = {
    'message': vcard_defs.MSG_INVALID_PARAM_NAME,
    'vcards': [
        _get_vcard_file('invalid_param_name.vcf')]}
VCARDS_INVALID_PARAM_VALUE = {
    'message': vcard_defs.MSG_INVALID_PARAM_VALUE,
    'vcards': [
        _get_vcard_file('invalid_param_value.vcf')]}
VCARDS_INVALID_PROPERTY_NAME = {
    'message': vcard_defs.MSG_INVALID_PROPERTY_NAME,
    'vcards': [
        _get_vcard_file('invalid_property_foo.vcf')]}
VCARDS_INVALID_SUBVALUE = {
    'message': vcard_defs.MSG_INVALID_SUBVALUE,
    'vcards': [
        ]}
VCARDS_INVALID_SUBVALUE_COUNT = {
    'message': vcard_defs.MSG_INVALID_SUBVALUE_COUNT,
    'vcards': [
        ]}
VCARDS_INVALID_TEXT_VALUE = {
    'message': vcard_defs.MSG_INVALID_TEXT_VALUE,
    'vcards': [
        ]}
VCARDS_INVALID_TIME = {
    'message': vcard_defs.MSG_INVALID_TIME,
    'vcards': [
        ]}
VCARDS_INVALID_TIME_ZONE = {
    'message': vcard_defs.MSG_INVALID_TIME_ZONE,
    'vcards': [
        ]}
VCARDS_INVALID_URI = {
    'message': vcard_defs.MSG_INVALID_URI,
    'vcards': [
        ]}
VCARDS_INVALID_VALUE = {
    'message': vcard_defs.MSG_INVALID_VALUE,
    'vcards': [
        _get_vcard_file('invalid_begin.vcf')]}
VCARDS_INVALID_VALUE_COUNT = {
    'message': vcard_defs.MSG_INVALID_VALUE_COUNT,
    'vcards': [
        # http://en.wikipedia.org/wiki/VCard
        _get_vcard_file('invalid_value_count_wp.vcf')]}
VCARDS_INVALID_X_NAME = {
    'message': vcard_defs.MSG_INVALID_X_NAME,
    'vcards': [
        ]}
VCARDS_MISMATCH_GROUP = {
    'message': vcard_defs.MSG_MISMATCH_GROUP,
    'vcards': [
        _get_vcard_file('mismatch_group.vcf')]}
VCARDS_MISMATCH_PARAM = {
    'message': vcard_defs.MSG_MISMATCH_PARAM,
    'vcards': [
        ]}
VCARDS_MISSING_GROUP = {
    'message': vcard_defs.MSG_MISSING_GROUP,
    'vcards': [
        _get_vcard_file('missing_group.vcf')]}
VCARDS_MISSING_PARAM = {
    'message': vcard_defs.MSG_MISSING_PARAM,
    'vcards': [
        _get_vcard_file('missing_photo_param.vcf')]}
VCARDS_MISSING_PARAM_VALUE = {
    'message': vcard_defs.MSG_MISSING_PARAM_VALUE,
    'vcards': [
        _get_vcard_file('missing_param_value.vcf')]}
VCARDS_MISSING_PROPERTY = {
    'message': vcard_defs.MSG_MISSING_PROPERTY,
    'vcards': [
        _get_vcard_file('missing_properties.vcf'),
        _get_vcard_file('missing_start.vcf'),
        _get_vcard_file('missing_end.vcf'),
        _get_vcard_file('missing_version.vcf'),
        _get_vcard_file('missing_n.vcf'),
        _get_vcard_file('missing_fn.vcf')]}
VCARDS_MISSING_VALUE_STRING = {
    'message': vcard_defs.MSG_MISSING_VALUE_STRING,
    'vcards': [
        _get_vcard_file('missing_n_value.vcf')]}
VCARDS_NON_EMPTY_PARAM = {
    'message': vcard_defs.MSG_NON_EMPTY_PARAM,
    'vcards': [
        ]}
VCARDS_WITH_ERROR = [
    VCARDS_CONTINUATION_AT_START,
    VCARDS_DOT_AT_LINE_START,
    VCARDS_EMPTY_VCARD,
    VCARDS_INVALID_DATE,
    VCARDS_INVALID_LANGUAGE_VALUE,
    VCARDS_INVALID_LINE_SEPARATOR,
    VCARDS_INVALID_PARAM_NAME,
    VCARDS_INVALID_PARAM_VALUE,
    VCARDS_INVALID_PROPERTY_NAME,
    VCARDS_INVALID_SUBVALUE,
    VCARDS_INVALID_SUBVALUE_COUNT,
    VCARDS_INVALID_TIME,
    VCARDS_INVALID_TIME_ZONE,
    VCARDS_INVALID_URI,
    VCARDS_INVALID_VALUE,
    VCARDS_INVALID_VALUE_COUNT,
    VCARDS_INVALID_X_NAME,
    VCARDS_MISMATCH_GROUP,
    VCARDS_MISMATCH_PARAM,
    VCARDS_MISSING_GROUP,
    VCARDS_MISSING_PARAM,
    VCARDS_MISSING_PARAM_VALUE,
    VCARDS_MISSING_PROPERTY,
    VCARDS_MISSING_VALUE_STRING,
    VCARDS_NON_EMPTY_PARAM]

# Reference cards with errors
VCARDS_REFERENCE_ERRORS = [
    _get_vcard_file('http://microformats.org/tests/hcard/01-tantek-basic.vcf'),
    _get_vcard_file('http://h2vx.com/vcf/tantek.com/%23contact'),
    # http://tools.ietf.org/html/rfc2426
    _get_vcard_file('rfc_2426_a.vcf'),
    _get_vcard_file('rfc_2426_b.vcf')]

# Valid vCards
VCARDS_VALID = [
    _get_vcard_file('minimal.vcf'),
    _get_vcard_file('maximal.vcf'),
    _get_vcard_file('scrambled_case.vcf'),
    _get_vcard_file('http://aspaass.no/kontakt/Aspaas%20Sykler.vcf'),
    _get_vcard_file(
        'http://www.troywolf.com/articles/php/class_vcard/vcard_example.php')]


class TestVCards(unittest.TestCase):
    """Test example vCards"""

    def test_failing(self):
        """vCards with errors"""
        for vcards in VCARDS_WITH_ERROR:
            for vcard_text in vcards['vcards']:
                try:
                    with warnings.catch_warnings(record=True):
                        vcard.VCard(vcard_text)
                        self.fail('Invalid vCard created:\n' + vcard_text)
                except vcard_validators.VCardFormatError as error:
                    message = str(error).splitlines()[0].split(':')[0]
                    self.assertEquals(
                        message,
                        vcards['message'],
                        'Wrong message for vCard:\n%s' % vcard_text + \
                        'Got "%s", expected "%s"' % (
                            message,
                            vcards['message']))


    def test_valid(self):
        """Valid (but not necessarily sane) vCards"""
        for vcard_text in VCARDS_VALID:
            try:
                with warnings.catch_warnings(record=True):
                    vc_obj = vcard.VCard(vcard_text)
                self.assertNotEqual(vc_obj, None)
            except vcard_validators.VCardFormatError as error:
                self.fail(
                    'Valid vCard not created:\n' + \
                    vcard_text + '\n' + \
                    str(error))


    def test_online(self):
        """vCards in references which are invalid"""
        for vcard_text in VCARDS_REFERENCE_ERRORS:
            with warnings.catch_warnings(record=True):
                self.assertRaises(
                    vcard_validators.VCardFormatError,
                    vcard.VCard,
                    vcard_text)


    def test_doc(self):
        """Documentation tests"""
        self.assertEqual(doctest.testmod(vcard)[0], 0)
        self.assertEqual(doctest.testmod(vcard_defs)[0], 0)
        self.assertEqual(doctest.testmod(vcard_utils)[0], 0)
        self.assertEqual(doctest.testmod(vcard_validators)[0], 0)

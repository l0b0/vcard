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

from vcard import (
    vcard,
    vcard_definitions,
    vcard_errors,
    vcard_utils,
    vcard_validators
)

TEST_DIRECTORY = os.path.dirname(__file__)


def _get_vcard_file(path):
    """
    Get the vCard contents locally or remotely.

    @param path: File relative to current directory or a URL
    @return: Text in the given file
    """
    if path in ('', None):
        return ''

    if path.startswith('http'):
        try:
            filename = urllib.urlretrieve(path)[0]
        except IOError:
            print('No internet connection; skipping {}\n'.format(path))
            return
    else:
        filename = os.path.join(TEST_DIRECTORY, path)

    with codecs.open(filename, 'r', 'utf-8') as file_pointer:
        contents = file_pointer.read()

    return contents


# vCards with errors
VCARDS_CONTINUATION_AT_START = {
    'message': vcard_errors.MSG_CONTINUATION_AT_START,
    'vcards': ('continuation_at_start.vcf',)}
VCARDS_DOT_AT_LINE_START = {
    'message': vcard_errors.MSG_DOT_AT_LINE_START,
    'vcards': ('dot_at_line_start.vcf',)}
VCARDS_EMPTY_VCARD = {
    'message': vcard_errors.MSG_EMPTY_VCARD,
    'vcards': (
        '',
        None)}
VCARDS_INVALID_DATE = {
    'message': vcard_errors.MSG_INVALID_DATE,
    'vcards': tuple()}
VCARDS_INVALID_LANGUAGE_VALUE = {
    'message': vcard_errors.MSG_INVALID_LANGUAGE_VALUE,
    'vcards': ('invalid_language_value.vcf',)}
VCARDS_INVALID_LINE_SEPARATOR = {
    'message': vcard_errors.MSG_INVALID_LINE_SEPARATOR,
    'vcards': (
        'line_ending_mac.vcf',
        'line_ending_unix.vcf',
        'line_ending_mixed.vcf',)}
VCARDS_INVALID_PARAM_NAME = {
    'message': vcard_errors.MSG_INVALID_PARAM_NAME,
    'vcards': ('invalid_param_name.vcf',)}
VCARDS_INVALID_PARAM_VALUE = {
    'message': vcard_errors.MSG_INVALID_PARAM_VALUE,
    'vcards': ('invalid_param_value.vcf',)}
VCARDS_INVALID_PROPERTY_NAME = {
    'message': vcard_errors.MSG_INVALID_PROPERTY_NAME,
    'vcards': ('invalid_property_foo.vcf',)}
VCARDS_INVALID_SUBVALUE = {
    'message': vcard_errors.MSG_INVALID_SUBVALUE,
    'vcards': tuple()}
VCARDS_INVALID_SUBVALUE_COUNT = {
    'message': vcard_errors.MSG_INVALID_SUBVALUE_COUNT,
    'vcards': tuple()}
VCARDS_INVALID_TEXT_VALUE = {
    'message': vcard_errors.MSG_INVALID_TEXT_VALUE,
    'vcards': tuple()}
VCARDS_INVALID_TIME = {
    'message': vcard_errors.MSG_INVALID_TIME,
    'vcards': tuple()}
VCARDS_INVALID_TIME_ZONE = {
    'message': vcard_errors.MSG_INVALID_TIME_ZONE,
    'vcards': tuple()}
VCARDS_INVALID_URI = {
    'message': vcard_errors.MSG_INVALID_URI,
    'vcards': tuple()}
VCARDS_INVALID_VALUE = {
    'message': vcard_errors.MSG_INVALID_VALUE,
    'vcards': (
        'invalid_begin.vcf',)}
VCARDS_INVALID_VALUE_COUNT = {
    'message': vcard_errors.MSG_INVALID_VALUE_COUNT,
    'vcards': (
        # http://en.wikipedia.org/wiki/VCard
        'invalid_value_count_wp.vcf',)}
VCARDS_INVALID_X_NAME = {
    'message': vcard_errors.MSG_INVALID_X_NAME,
    'vcards': tuple()}
VCARDS_MISMATCH_GROUP = {
    'message': vcard_errors.MSG_MISMATCH_GROUP,
    'vcards': (
        'mismatch_group.vcf',)}
VCARDS_MISMATCH_PARAM = {
    'message': vcard_errors.MSG_MISMATCH_PARAM,
    'vcards': tuple()}
VCARDS_MISSING_GROUP = {
    'message': vcard_errors.MSG_MISSING_GROUP,
    'vcards': (
        'missing_group.vcf',)}
VCARDS_MISSING_PARAM = {
    'message': vcard_errors.MSG_MISSING_PARAM,
    'vcards': (
        'missing_photo_param.vcf',)}
VCARDS_MISSING_PARAM_VALUE = {
    'message': vcard_errors.MSG_MISSING_PARAM_VALUE,
    'vcards': (
        'missing_param_value.vcf',)}
VCARDS_MISSING_PROPERTY = {
    'message': vcard_errors.MSG_MISSING_PROPERTY,
    'vcards': (
        'missing_properties.vcf',
        'missing_start.vcf',
        'missing_end.vcf',
        'missing_version.vcf',
        'missing_n.vcf',
        'missing_fn.vcf',)}
VCARDS_MISSING_VALUE_STRING = {
    'message': vcard_errors.MSG_MISSING_VALUE_STRING,
    'vcards': (
        'missing_n_value.vcf',)}
VCARDS_NON_EMPTY_PARAM = {
    'message': vcard_errors.MSG_NON_EMPTY_PARAM,
    'vcards': (
        'http://aspaass.no/kontakt/Aspaas%20Sykler.vcf',
        'http://www.troywolf.com/articles/php/class_vcard/vcard_example.php')}

VCARDS_WITH_ERROR = (
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
    VCARDS_NON_EMPTY_PARAM)

# Reference cards with errors
VCARDS_REFERENCE_ERRORS = (
    'http://microformats.org/tests/hcard/01-tantek-basic.vcf',
    'http://h2vx.com/vcf/tantek.com/%23contact',

    # http://tools.ietf.org/html/rfc2426
    'rfc_2426_a.vcf',
    'rfc_2426_b.vcf'
)

# Valid vCards
VCARDS_VALID = (
    'minimal.vcf',
    'maximal.vcf',
    'scrambled_case.vcf'
)


class TestVCards(unittest.TestCase):
    """Test example vCards"""

    def test_failing(self):
        """vCards with errors"""
        for testgroup in VCARDS_WITH_ERROR:
            for vcard_file in testgroup['vcards']:
                vcard_text = _get_vcard_file(vcard_file)
                if vcard_text is None:
                    continue

                try:
                    with warnings.catch_warnings(record=True):
                        vcard.VCard(vcard_text, filename=vcard_file)
                        self.fail('Invalid vCard created:\n{0}'.format(vcard_text))
                except vcard_errors.VCardError as error:
                    error_msg = '\n\n'.join((
                        'Wrong message for vCard {vcard_file!r}:'.format(vcard_file=vcard_file),
                        'Expected: {expected}'.format(expected=testgroup['message']),
                        'Got: {got}'.format(got=str(error)),
                        ))
                    self.assertTrue(
                        testgroup['message'] in str(error),
                        msg=error_msg
                    )

    def test_valid(self):
        """Valid (but not necessarily sane) vCards"""
        for vcard_file in VCARDS_VALID:
            vcard_text = _get_vcard_file(vcard_file)
            if vcard_text is None:
                continue

            try:
                with warnings.catch_warnings(record=True):
                    vc_obj = vcard.VCard(vcard_text, filename=vcard_file)
                self.assertNotEqual(vc_obj, None)
            except vcard_errors.VCardError as error:
                error_msg = '\n\n'.join((
                    'Expected valid vCard for {vcard_file!r}, but it failed to validate'.format(
                        vcard_file=vcard_file
                    ),
                    str(error)
                ))
                self.fail(error_msg)

    def test_online(self):
        """vCards in references which are invalid"""
        for vcard_file in VCARDS_REFERENCE_ERRORS:
            vcard_text = _get_vcard_file(vcard_file)
            if vcard_text is None:
                continue

            with warnings.catch_warnings(record=True):
                self.assertRaises(
                    vcard_errors.VCardError,
                    vcard.VCard,
                    vcard_text)

    def test_doc(self):
        """Run DocTests"""
        self.assertEqual(doctest.testmod(vcard)[0], 0)
        self.assertEqual(doctest.testmod(vcard_definitions)[0], 0)
        self.assertEqual(doctest.testmod(vcard_errors)[0], 0)
        self.assertEqual(doctest.testmod(vcard_utils)[0], 0)
        self.assertEqual(doctest.testmod(vcard_validators)[0], 0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for vcard module

Default syntax:

./vcard_test.py
    Run all unit tests
"""
import codecs
import doctest
import os
import sys
import unittest
import urllib
import warnings

import vcard

# pylint: disable-msg=C0301
# Invalid vCards
VCARD_EMPTY = ''
VCARDS_MISSING = {
    'properties': 'BEGIN:VCARD\r\nEND:VCARD\r\n',
    'start': 'VERSION:3.0\r\nN:Doe;John;Ottoman;Mr;\r\nFN:John Ottoman Doe\r\nEND:VCARD\r\n',
    'end': 'BEGIN:VCARD\r\nVERSION:3.0\r\nN:Doe;John;Ottoman;Mr;\r\nFN:John Ottoman Doe\r\n',
    'version': 'BEGIN:VCARD\r\nN:Doe;John;Ottoman;Mr;Jr\r\nFN:John Ottoman Doe\r\nEND:VCARD\r\n',
    'n': 'BEGIN:VCARD\r\nVERSION:3.0\r\nFN:John Doe\r\nEND:VCARD\r\n',
    'fn': 'BEGIN:VCARD\r\nVERSION:3.0\r\nN:Doe;John;;Mr;\r\nEND:VCARD\r\n'}
VCARDS_INVALID_PROPERTY_NAME = {
    'foobar': 'BEGIN:VCARD\r\nVERSION:3.0\r\nFOO:bar\r\nN:Doe;John;;Mr;\r\nFN:John Doe\r\nEND:VCARD\r\n'}
VCARDS_INVALID_PARAM = {
    }
VCARDS_INVALID_PARAM_VALUE = {
    }
VCARDS_INVALID_VALUE = {
    'http://en.wikipedia.org/wiki/VCard': u"""BEGIN:VCARD\r\nVERSION:3.0\r\nN:Gump;Forrest\r\nFN:Forrest Gump\r\nORG:Bubba Gump Shrimp Co.\r\nTITLE:Shrimp Man\r\nTEL;TYPE=WORK,VOICE:(111) 555-1212\r\nTEL;TYPE=HOME,VOICE:(404) 555-1212\r\nADR;TYPE=WORK:;;100 Waters Edge;Baytown;LA;30314;United States of America\r\nLABEL;TYPE=WORK:100 Waters Edge\\nBaytown, LA 30314\\nUnited States of America\r\nADR;TYPE=HOME:;;42 Plantation St.;Baytown;LA;30314;United States of America\r\nLABEL;TYPE=HOME:42 Plantation St.\\nBaytown, LA 30314\\nUnited States of America\r\nEMAIL;TYPE=PREF,INTERNET:forrestgump@example.com\r\nREV:20080424T195243Z\r\nEND:VCARD\r\n""",
    'http://microformats.org/tests/hcard/01-tantek-basic.vcf': u"""BEGIN:VCARD\r\nFN;CHARSET=UTF-8:Tantek Çelik\r\nN;CHARSET=UTF-8:Çelik;Tantek;;;\r\nNAME:01-tantek-basic\r\nORG;CHARSET=UTF-8:Technorati\r\nPRODID:$PRODID$\r\nSOURCE:http://microformats.org/test/hcard/01-tantek-basic.html\r\nURL:http://tantek.com/\r\nVERSION:3.0\r\nEND:VCARD\r\n""",
    }

# Valid vCards
minimal_file = codecs.open(
    os.path.join(os.path.dirname(__file__), 'minimal.vcf'),
    'r',
    'utf-8').read()

scrambled_case_file = codecs.open(
    os.path.join(os.path.dirname(__file__), 'scrambled_case.vcf'),
    'r',
    'utf-8').read()

aspaass_filename = urllib.urlretrieve(
    'http://aspaass.no/kontakt/Aspaas%20Sykler.vcf',
    os.path.join(os.path.dirname(__file__), 'Aspaas Sykler.vcf'))[0]
aspaass_file = codecs.open(aspaass_filename, 'r', 'utf-8').read()

troywolf_filename = urllib.urlretrieve(
    'http://www.troywolf.com/articles/php/class_vcard/vcard_example.php',
    os.path.join(os.path.dirname(__file__), 'troywolf.vcf'))[0]
troywolf_file = codecs.open(troywolf_filename, 'r', 'utf-8').read()

VCARDS_VALID = {
    'minimal': minimal_file,
    'scrambled case': scrambled_case_file,
    'Aspaas Sykler': aspaass_file,
    'Troy Wolf': troywolf_file,
    }

rfc_2426_a_file = codecs.open(
    os.path.join(os.path.dirname(__file__), 'rfc_2426_a.vcf'),
    'r',
    'utf-8').read()

rfc_2426_b_file = codecs.open(
    os.path.join(os.path.dirname(__file__), 'rfc_2426_b.vcf'),
    'r',
    'utf-8').read()

VCARDS_REFERENCE = {
    'http://tools.ietf.org/html/rfc2426 1': rfc_2426_a_file,
    'http://tools.ietf.org/html/rfc2426 2': rfc_2426_b_file}

# pylint: enable-msg=C0301

class TestVCards(unittest.TestCase):
    """Test small vCards"""
    def test_empty(self):
        """Empty string"""
        try:
            vcard.VCard(VCARD_EMPTY)
            self.fail('Invalid vCard created')
        except vcard.VCardFormatError as error:
            self.assertEquals(error.message, vcard.MSG_EMPTY_VCARD)

    def test_missing(self):
        """vCards missing a mandatory property"""
        for vcard_title, vcard_text in VCARDS_MISSING.items():
            try:
                vcard.VCard(vcard_text)
                self.fail('Invalid vCard "%s" created' % vcard_title)
            except vcard.VCardFormatError as error:
                self.assertEquals(
                    error.message[:len(vcard.MSG_MISSING_PROPERTY)],
                    vcard.MSG_MISSING_PROPERTY)

    def test_valid(self):
        """Valid (but not necessarily sane) vCards"""
        for vcard_title, vcard_text in VCARDS_VALID.items():
            try:
                with warnings.catch_warnings(record=True):
                    vc_obj = vcard.VCard(vcard_text)
                self.assertNotEqual(vc_obj, None)
            except vcard.VCardFormatError as error:
                self.fail(
                    'Valid vCard "%s" not created' % vcard_title + '\n' + \
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
            except vcard.VCardFormatError:
                pass
                #self.fail(
                #    'Valid vCard "%s" not created' % vcard_title + '\n' + \
                #    error.message)

    def test_doc(self):
        """
        Documentation tests
        """
        doctest.testmod(vcard)

def main():
    """Command line options checkpoint"""
    unittest.main()

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
from unittest import TestCase

from vcard.vcard_errors import VCardError


class TestVCardError(TestCase):
    def test_empty_context_output(self):
        actual = str(VCardError('message', {}))
        expected = 'message'
        self.assertEqual(expected, actual)

    def test_single_context_item_output(self):
        context = {'File': '/home/user/test.vcf'}
        actual = str(VCardError('message', context))
        expected = 'message\nFile: /home/user/test.vcf'
        self.assertEqual(expected, actual)

    def test_full_context_output(self):
        context = {
            'File': '/home/user/test.vcf',
            'File line': 120,
            'vCard line': 5,
            'Property': 'ADR',
            'Property line': 2,
            'String': 'too;few;values;êéè'
        }
        actual = str(VCardError('message', context))
        expected = '\n'.join([
            'message',
            'File: /home/user/test.vcf',
            'File line: 120',
            'vCard line: 5',
            'Property: ADR',
            'Property line: 2',
            'String: too;few;values;êéè',
        ])
        self.assertEqual(expected, actual)

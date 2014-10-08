#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vCard v3.0 (RFC 2426) definitions and message strings"""


def character_range(start, end):
    return u"".join(unichr(index) for index in range(start, end + 1))

# Literals, RFC 2426 pages 27, 28
ALPHA_CHARACTERS = character_range(0x41, 0x5A) + character_range(0x61, 0x7A)
CARRIAGE_RETURN_CHARACTER = unichr(0x0D)
LINE_FEED_CHARACTER = unichr(0x0A)
NEWLINE_CHARACTERS = CARRIAGE_RETURN_CHARACTER + LINE_FEED_CHARACTER
CONTROL_CHARACTERS = character_range(0x00, 0x1F) + unichr(0x7F)
DIGIT_CHARACTERS = character_range(0x30, 0x39)
DOUBLE_QUOTE_CHARACTER = unichr(0x22)
HORIZONTAL_TAB_CHARACTER = unichr(0x09)
SPACE_CHARACTER = unichr(0x20)
PRINTABLE_CHARACTERS = character_range(0x21, 0x7E)
WHITESPACE_CHARACTERS = SPACE_CHARACTER + HORIZONTAL_TAB_CHARACTER
NON_ASCII_CHARACTERS = character_range(0x80, 0xFF)

# Have to remove backslash!
QUOTE_SAFE_CHARACTERS = \
    WHITESPACE_CHARACTERS + unichr(0x21) + character_range(0x23, 0x5B) + character_range(0x5D, 0x7E) + \
    NON_ASCII_CHARACTERS
SAFE_CHARACTERS = WHITESPACE_CHARACTERS + unichr(0x21) + character_range(0x23, 0x2B) + character_range(0x2D, 0x39) + \
    character_range(0x3C, 0x5B) + character_range(0x5D, 0x7E) + NON_ASCII_CHARACTERS
VALUE_CHARACTERS = WHITESPACE_CHARACTERS + PRINTABLE_CHARACTERS + NON_ASCII_CHARACTERS
ESCAPED_CHARACTERS = u'\\;,nN'

# Known property names (RFC 2426 page 4)
MANDATORY_PROPERTIES = ['BEGIN', 'END', 'FN', 'N', 'VERSION']
PREDEFINED_PROPERTIES = ['BEGIN', 'END', 'NAME', 'PROFILE', 'SOURCE']
OTHER_PROPERTIES = [
    'ADR', 'AGENT', 'BDAY', 'CATEGORIES', 'CLASS', 'EMAIL', 'GEO', 'KEY', 'LABEL', 'LOGO', 'MAILER', 'NICKNAME', 'NOTE',
    'ORG', 'PHOTO', 'PRODID', 'REV', 'ROLE', 'SORT-STRING', 'SOUND', 'TEL', 'TITLE', 'TZ', 'UID', 'URL']
ALL_PROPERTIES = list(set(MANDATORY_PROPERTIES + PREDEFINED_PROPERTIES + OTHER_PROPERTIES))

# IDs for group, name, iana-token, x-name, param-name (RFC 2426 page 29)
ID_CHARACTERS = ALPHA_CHARACTERS + DIGIT_CHARACTERS + '-'

VCARD_LINE_MAX_LENGTH = 75
"""RFC 2426 page 6"""

VCARD_LINE_MAX_LENGTH_RAW = VCARD_LINE_MAX_LENGTH + len(NEWLINE_CHARACTERS)
"""Including line ending"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vCards v3.0 (RFC 2426) definitions and message strings"""


def character_range(start, end):
    return u"".join(unichr(index) for index in range(start, end + 1))

# Literals, RFC 2426 pages 27, 28
ALPHA_CHARS = character_range(0x41, 0x5A) + character_range(0x61, 0x7A)
CR_CHAR = unichr(0x0D)
LF_CHAR = unichr(0x0A)
CRLF_CHARS = CR_CHAR + LF_CHAR
CTL_CHARS = character_range(0x00, 0x1F) + unichr(0x7F)
DIGIT_CHARS = character_range(0x30, 0x39)
DQUOTE_CHAR = unichr(0x22)
HTAB_CHAR = unichr(0x09)
SP_CHAR = unichr(0x20)
VCHAR_CHARS = character_range(0x21, 0x7E)
WSP_CHARS = SP_CHAR + HTAB_CHAR
NON_ASCII_CHARS = character_range(0x80, 0xFF)

# Have to remove backslash!
QSAFE_CHARS = WSP_CHARS + unichr(0x21) + character_range(0x23, 0x5B) + character_range(0x5D, 0x7E) + NON_ASCII_CHARS
SAFE_CHARS = WSP_CHARS + unichr(0x21) + character_range(0x23, 0x2B) + character_range(0x2D, 0x39) + \
    character_range(0x3C, 0x5B) + character_range(0x5D, 0x7E) + NON_ASCII_CHARS
VALUE_CHARS = WSP_CHARS + VCHAR_CHARS + NON_ASCII_CHARS
ESCAPED_CHARS = u'\\;,nN'

# Known property names (RFC 2426 page 4)
MANDATORY_PROPERTIES = ['BEGIN', 'END', 'FN', 'N', 'VERSION']
PREDEFINED_PROPERTIES = ['BEGIN', 'END', 'NAME', 'PROFILE', 'SOURCE']
OTHER_PROPERTIES = [
    'ADR', 'AGENT', 'BDAY', 'CATEGORIES', 'CLASS', 'EMAIL', 'GEO', 'KEY', 'LABEL', 'LOGO', 'MAILER', 'NICKNAME', 'NOTE',
    'ORG', 'PHOTO', 'PRODID', 'REV', 'ROLE', 'SORT-STRING', 'SOUND', 'TEL', 'TITLE', 'TZ', 'UID', 'URL']
ALL_PROPERTIES = list(set(MANDATORY_PROPERTIES + PREDEFINED_PROPERTIES + OTHER_PROPERTIES))

# IDs for group, name, iana-token, x-name, param-name (RFC 2426 page 29)
ID_CHARS = ALPHA_CHARS + DIGIT_CHARS + '-'

VCARD_LINE_MAX_LENGTH = 75
"""RFC 2426 page 6"""

VCARD_LINE_MAX_LENGTH_RAW = VCARD_LINE_MAX_LENGTH + len(CRLF_CHARS)
"""Including line ending"""

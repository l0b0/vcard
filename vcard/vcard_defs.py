#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vCards v3.0 (RFC 2426) definitions and message strings"""


def character_range(start, end):
    return u"".join(unichr(index) for index in range(start, end + 1))

# Literals, RFC 2426 pages 27, 28
ALPHA_CHARS = character_range(0x41, 0x5A) + character_range(0x61, 0x7A)
CHAR_CHARS = character_range(0x01, 0x7F)
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
    'ADR', 'AGENT', 'BDAY', 'CATEGORIES', 'CLASS', 'EMAIL', 'GEO', 'KEY',
    'LABEL', 'LOGO', 'MAILER', 'NICKNAME', 'NOTE', 'ORG', 'PHOTO', 'PRODID',
    'REV', 'ROLE', 'SORT-STRING', 'SOUND', 'TEL', 'TITLE', 'TZ', 'UID', 'URL']
ALL_PROPERTIES = list(
    set(
        MANDATORY_PROPERTIES + PREDEFINED_PROPERTIES + OTHER_PROPERTIES))

# IDs for group, name, iana-token, x-name, param-name (RFC 2426 page 29)
ID_CHARS = ALPHA_CHARS + DIGIT_CHARS + '-'

VCARD_LINE_MAX_LENGTH = 75
"""RFC 2426 page 6"""

VCARD_LINE_MAX_LENGTH_RAW = VCARD_LINE_MAX_LENGTH + len(CRLF_CHARS)
"""Including line ending"""

# Error literals
MSG_CONTINUATION_AT_START = 'Continuation line at start of vCard (See RFC \
2425 section 5.8.1 for line folding details)'
MSG_DOT_AT_LINE_START = 'Dot at start of line without group name (See RFC \
2426 section 4 for group syntax)'
MSG_EMPTY_VCARD = 'vCard is empty'
MSG_INVALID_DATE = 'Invalid date (See RFC 2425 section 5.8.4 for date syntax)'
MSG_INVALID_LANGUAGE_VALUE = 'Invalid language (See RFC 1766 section 2 for \
details)'
MSG_INVALID_LINE_SEPARATOR = 'Invalid line ending; should be \\r\\n (See RFC \
2426 section 2.4.2 for details)'
MSG_INVALID_PARAM_NAME = 'Invalid parameter name (See RFC 2426 section 4 for \
param-name syntax)'
MSG_INVALID_PARAM_VALUE = 'Invalid parameter value (See RFC 2426 section 4 \
for param-value syntax)'
MSG_INVALID_PROPERTY_NAME = 'Invalid property name (See RFC 2426 section 4 \
for name syntax)'
MSG_INVALID_SUBVALUE = 'Invalid subvalue (See RFC 2426 section 3 for details)'
MSG_INVALID_SUBVALUE_COUNT = 'Invalid subvalue count (See RFC 2426 section 3 \
for details)'
MSG_INVALID_TEXT_VALUE = 'Invalid text value (See RFC 2426 section 4 for \
details)'
MSG_INVALID_TIME = 'Invalid time (See RFC 2425 section 5.8.4 for time syntax)'
MSG_INVALID_TIME_ZONE = 'Invalid time zone (See RFC 2426 section 3.4.1 for \
time-zone syntax)'
MSG_INVALID_URI = 'Invalid URI (See RFC 1738 section 5 for genericurl syntax)'
MSG_INVALID_VALUE = 'Invalid value (See RFC 2426 section 3 for details)'
MSG_INVALID_VALUE_COUNT = 'Invalid value count (See RFC 2426 section 3 for \
details)'
MSG_INVALID_X_NAME = 'Invalid X-name (See RFC 2426 section 4 for x-name \
syntax)'
MSG_MISMATCH_GROUP = 'Group mismatch (See RFC 2426 section 4 for contentline \
syntax)'
MSG_MISMATCH_PARAM = 'Parameter mismatch (See RFC 2426 section 3 for details)'
MSG_MISSING_GROUP = 'Missing group (See RFC 2426 section 4 for contentline \
syntax)'
MSG_MISSING_PARAM = 'Parameter missing (See RFC 2426 section 3 for details)'
MSG_MISSING_PARAM_VALUE = 'Parameter value missing (See RFC 2426 section 3 \
for details)'
MSG_MISSING_PROPERTY = 'Mandatory property missing (See RFC 2426 section 5 \
for details)'
MSG_MISSING_VALUE_STRING = 'Missing value string (See RFC 2426 section 4 for \
contentline syntax)'
MSG_NON_EMPTY_PARAM = 'Property should not have parameters (See RFC 2426 \
section 3 for details)'

# Warning literals
WARN_DEFAULT_TYPE_VALUE = 'Using default TYPE value; can be removed'
WARN_INVALID_DATE = 'Possible invalid date'
WARN_INVALID_EMAIL_TYPE = 'Possible invalid email TYPE'
WARN_MULTIPLE_NAMES = 'Possible split name (replace space with comma)'

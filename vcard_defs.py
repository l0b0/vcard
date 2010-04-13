#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vCards v3.0 (RFC 2426) definitions and message strings"""

# pylint: disable-msg=W0105

# Literals, RFC 2426 pages 27, 28
ALPHA_CHARS = u'\u0041-\u005A\u0061-\u007A'
CHAR_CHARS = u'\u0001-\u007F'
CR_CHAR = u'\u000D'
LF_CHAR = u'\u000A'
CRLF_CHARS = CR_CHAR + LF_CHAR
CTL_CHARS = u'\u0000-\u001F\u007F'
DIGIT_CHARS = u'\u0030-\u0039'
DQUOTE_CHAR = u'\u0022'
HTAB_CHAR = u'\u0009'
SP_CHAR = u'\u0020'
VCHAR_CHARS = u'\u0021-\u007E'
WSP_CHARS = SP_CHAR + HTAB_CHAR
NON_ASCII_CHARS = u'\u0080-\u00FF'
QSAFE_CHARS = WSP_CHARS + u'\u0021' + u'\u0023-\u007E' + NON_ASCII_CHARS
SAFE_CHARS = WSP_CHARS + u'\u0021' + u'\u0023-\u002B' + u'\u002D-\u0039' + \
             u'\u003C-\u007E' + NON_ASCII_CHARS
VALUE_CHARS = WSP_CHARS + VCHAR_CHARS + NON_ASCII_CHARS

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
MSG_CONTINUATION_AT_START = 'Continuation line at start of vCard'
MSG_DOT_AT_LINE_START = 'Dot at start of line without group name'
MSG_EMPTY_LINE = 'Empty line found'
MSG_EMPTY_VCARD = 'vCard is empty'
MSG_INVALID_DATE = 'Invalid date'
MSG_INVALID_FIRST_LINE = 'Invalid first line'
MSG_INVALID_LANGUAGE_VALUE = 'Invalid language'
MSG_INVALID_LAST_LINE = 'Invalid last line'
MSG_INVALID_LINE_SEPARATOR = 'Invalid line ending; should be CRLF (\\r\\n)'
MSG_INVALID_PARAM_NAME = 'Invalid parameter name'
MSG_INVALID_PARAM_VALUE = 'Invalid parameter value'
MSG_INVALID_PROPERTY_NAME = 'Invalid property name'
MSG_INVALID_SUBVALUE = 'Invalid subvalue'
MSG_INVALID_SUBVALUE_COUNT = 'Invalid subvalue count'
MSG_INVALID_TIME = 'Invalid time'
MSG_INVALID_TIME_ZONE = 'Invalid time zone'
MSG_INVALID_VALUE = 'Invalid value'
MSG_INVALID_VALUE_COUNT = 'Invalid value count'
MSG_INVALID_X_NAME = 'Invalid X-name'
MSG_MISMATCH_GROUP = 'Group mismatch'
MSG_MISMATCH_PARAM = 'Parameter mismatch'
MSG_MISSING_GROUP = 'Missing group'
MSG_MISSING_PARAM = 'Parameter missing'
MSG_MISSING_PARAM_VALUE = 'Parameter value missing'
MSG_MISSING_PROPERTY = 'Mandatory property missing'
MSG_MISSING_VALUE_STRING = 'Missing value string'
MSG_NON_EMPTY_PARAM = 'Property should not have parameters'

# Warning literals
WARN_DEFAULT_TYPE_VALUE = 'Using default TYPE value; can be removed'
WARN_INVALID_DATE = 'Possible invalid date'
WARN_INVALID_EMAIL_TYPE = 'Possible invalid email TYPE'
WARN_MULTIPLE_NAMES = 'Possible split name (replace space with comma)'

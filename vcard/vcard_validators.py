#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vCards v3.0 (RFC 2426) validating functions

Should contain all the general purpose validation code extracted from
standards.
"""

import re
from urlparse import urlparse
import warnings

# Third party modules
import isodate

# Local modules
from vcard_definitions import DQUOTE_CHAR, ID_CHARS, ESCAPED_CHARS, QSAFE_CHARS, SAFE_CHARS, SP_CHAR

from vcard_errors import (
    # Error literals
    MSG_INVALID_DATE,
    MSG_INVALID_LANGUAGE_VALUE,
    MSG_INVALID_PARAM_NAME,
    MSG_INVALID_PARAM_VALUE,
    MSG_INVALID_SUBVALUE,
    MSG_INVALID_SUBVALUE_COUNT,
    MSG_INVALID_TEXT_VALUE,
    MSG_INVALID_TIME,
    MSG_INVALID_TIME_ZONE,
    MSG_INVALID_URI,
    MSG_INVALID_VALUE,
    MSG_INVALID_VALUE_COUNT,
    MSG_INVALID_X_NAME,
    MSG_MISMATCH_PARAM,
    MSG_MISSING_PARAM,
    MSG_NON_EMPTY_PARAM,
    WARN_DEFAULT_TYPE_VALUE,
    WARN_INVALID_EMAIL_TYPE,
    WARN_MULTIPLE_NAMES,
    # Functions
    show_warning,
    # Classes
    VCardError,
    VCardItemCountError,
    VCardNameError,
    VCardValueError
)

VALID_DATE = re.compile(r'^\d{4}-?\d{2}-?\d{2}$')
VALID_TZ = re.compile(r'^(Z|[+-]\d{2}:?\d{2})$')
VALID_TIME_TZ = re.compile(r'^(\d{2}:?\d{2}:?\d{2}(?:,\d+)?)(.*)$')
VALID_LANG_TAG = re.compile(r'^([a-z]{1,8})(-[a-z]{1,8})*$')
VALID_X_NAME = re.compile(r'^X-[{0}]+$'.format(re.escape(ID_CHARS)))
VALID_PTEXT = re.compile(u'^[{0}]*$'.format(re.escape(SAFE_CHARS)))
VALID_TEXT = re.compile(u'^([{0}:{1}]|(\\\\[{2}]))*$'.format(
    re.escape(SAFE_CHARS), DQUOTE_CHAR, re.escape(ESCAPED_CHARS)))
VALID_QUOTED_STRING = re.compile(u'^{0}[{1}]{0}$'.format(DQUOTE_CHAR, re.escape(QSAFE_CHARS)))
VALID_FLOAT = re.compile(r'^[+-]?\d+(\.\d+)?$')

LABEL_TYPE_VALUES = ('dom', 'intl', 'postal', 'parcel', 'home', 'work', 'pref')
TELEPHONE_TYPE_VALUES = (
    'home', 'msg', 'work', 'pref', 'voice', 'fax', 'cell', 'video', 'pager', 'bbs', 'modem', 'car', 'isdn', 'pcs')
EMAIL_TYPE_VALUES = ('internet', 'x400', 'pref', 'dom', 'intl', 'postal', 'parcel', 'home', 'work')


def _expect_no_params(prop):
    if 'parameters' in prop:
        raise VCardItemCountError('{0}: {1[parameters]}'.format(MSG_NON_EMPTY_PARAM, prop), {})


def _expect_params(prop):
    if 'parameters' not in prop:
        raise VCardItemCountError(MSG_MISSING_PARAM, {})


def _expect_value_count(values, count):
    if len(values) != count:
        raise VCardItemCountError('{0}: {1:d} (expected {2})'.format(MSG_INVALID_VALUE_COUNT, len(values), count), {})


def _expect_subvalue_count(subvalues, count):
    if len(subvalues) != count:
        raise VCardItemCountError(
            '{0}: {1:d} (expected {2})'.format(MSG_INVALID_SUBVALUE_COUNT, len(subvalues), count), {})


def validate_date(text):
    """
    Based on http://tools.ietf.org/html/rfc2425#section-5.8.4 and the fact
    that it specifies a subset of ISO 8601.

    @param text: String

    Examples:
    >>> validate_date('20000101')
    >>> validate_date('2000-01-01')
    >>> validate_date('2000:01:01') # Wrong separator
    Traceback (most recent call last):
    VCardValueError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 2000:01:01
    >>> validate_date('2000101') # Too short
    Traceback (most recent call last):
    VCardValueError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 2000101
    >>> validate_date('20080229')
    >>> validate_date('20100229') # Not a leap year
    Traceback (most recent call last):
    VCardValueError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 20100229
    >>> validate_date('19000229') # Not a leap year (divisible by 100)
    Traceback (most recent call last):
    VCardValueError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 19000229
    >>> validate_date('20000229') # Leap year (divisible by 400)
    >>> validate_date('aaaa-bb-cc')
    Traceback (most recent call last):
    VCardValueError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: aaaa-bb-cc
    """
    if VALID_DATE.match(text) is None:
        raise VCardValueError(MSG_INVALID_DATE, {'String': text})

    try:
        isodate.parse_date(text)
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(MSG_INVALID_DATE, {'String': text})


def validate_time_zone(text):
    """
    Based on http://tools.ietf.org/html/rfc2425#section-5.8.4 and the fact
    that it specifies a subset of ISO 8601.

    @param text: String

    Examples:
    >>> validate_time_zone('Z')
    >>> validate_time_zone('+01:00')
    >>> validate_time_zone('-12:30')
    >>> validate_time_zone('+23:59')
    >>> validate_time_zone('-0001')
    >>> validate_time_zone('-00:30')
    >>> validate_time_zone('+00:30')
    >>> validate_time_zone('Z+01:00') # Can't combine Z and offset
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: Z+01:00
    >>> validate_time_zone('+1:00') # Need preceding zero
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: +1:00
    >>> validate_time_zone('0100') # Need + or -
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: 0100
    >>> validate_time_zone('01') # Need colon and minutes
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: 01
    >>> validate_time_zone('01:') # Need minutes
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: 01:
    >>> validate_time_zone('01:1') # Need preceding zero
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    """
    if not VALID_TZ.match(text):
        raise VCardValueError(MSG_INVALID_TIME_ZONE, {'String': text})

    try:
        isodate.parse_tzinfo(text.replace('+', 'Z+').replace('-', 'Z-'))
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(MSG_INVALID_TIME_ZONE, {'String': text})


def validate_time(text):
    """
    Based on http://tools.ietf.org/html/rfc2425#section-5.8.4 and the fact
    that it specifies a subset of ISO 8601.

    @param text: String

    Examples:
    >>> validate_time('00:00:00')
    >>> validate_time('000000')
    >>> validate_time('01:02:03Z')
    >>> validate_time('01:02:03+01:30')
    >>> validate_time('01:02:60')
    Traceback (most recent call last):
    VCardValueError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 01:02:60
    >>> validate_time('01:60:59')
    Traceback (most recent call last):
    VCardValueError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 01:60:59
    >>> validate_time('24:00:00')
    Traceback (most recent call last):
    VCardValueError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 24:00:00
    >>> validate_time('00:00:00Z+01') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid time zone ...
    String: Z+01
    """
    time_timezone = VALID_TIME_TZ.match(text)
    if time_timezone is None:
        raise VCardValueError(MSG_INVALID_TIME, {'String': text})

    time_str, timezone_str = time_timezone.groups()
    try:
        isodate.parse_time(time_str)
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(MSG_INVALID_TIME, {'String': text})

    if timezone_str == '':
        return

    validate_time_zone(timezone_str)


def validate_language_tag(text):
    """
    langval, as defined by RFC 1766 <http://tools.ietf.org/html/rfc1766>

    @param text: String

    Examples:
    >>> validate_language_tag('en')
    >>> validate_language_tag('-US') # Need primary tag
    Traceback (most recent call last):
    VCardValueError: Invalid language (See RFC 1766 section 2 for details)
    String: -us
    >>> validate_language_tag('en-') # Can't end with dash
    Traceback (most recent call last):
    VCardValueError: Invalid language (See RFC 1766 section 2 for details)
    String: en-
    >>> validate_language_tag('en-US')

    """
    text = text.lower()  # Case insensitive

    if VALID_LANG_TAG.match(text) is None:
        raise VCardValueError(MSG_INVALID_LANGUAGE_VALUE, {'String': text})

    # TODO: Extend to validate according to referenced ISO/RFC standards


def validate_x_name(text):
    """
    @param text: Single parameter name

    Examples:
    >>> validate_x_name('X-abc')
    >>> validate_x_name('X-' + ID_CHARS)
    >>> validate_x_name('X-') # Have to have more characters
    Traceback (most recent call last):
    VCardNameError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: X-
    >>> validate_x_name('') # Have to start with X- #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    VCardNameError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    ...
    >>> validate_x_name('x-abc') # X must be upper case
    Traceback (most recent call last):
    VCardNameError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: x-abc
    >>> validate_x_name('foo') # Have to start with X-
    Traceback (most recent call last):
    VCardNameError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: foo
    """
    if VALID_X_NAME.match(text) is None:
        raise VCardNameError(MSG_INVALID_X_NAME, {'String': text})


def validate_ptext(text):
    """
    ptext, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_ptext('')
    >>> validate_ptext(SAFE_CHARS)
    >>> validate_ptext(u'\u000B') #doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: ...
    """
    if VALID_PTEXT.match(text) is None:
        raise VCardValueError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_text_value(text):
    """
    text-value, as described on page 37
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_text_value('')
    >>> validate_text_value('\\\\,')
    >>> validate_text_value(SAFE_CHARS)
    >>> validate_text_value('\\\\n')
    >>> validate_text_value(';') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid text value (See RFC 2426 section 4 for details)
    String: ...
    >>> validate_text_value('\\\\\\\\;') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid text value (See RFC 2426 section 4 for details)
    String: ...
    """
    if VALID_TEXT.match(text) is None:
        raise VCardValueError(MSG_INVALID_TEXT_VALUE, {'String': text})


def validate_quoted_string(text):
    """
    quoted-string, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_quoted_string(DQUOTE_CHAR + QSAFE_CHARS[0] + DQUOTE_CHAR)
    >>> validate_quoted_string(DQUOTE_CHAR + DQUOTE_CHAR) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    >>> validate_quoted_string(
    ... DQUOTE_CHAR + QSAFE_CHARS[-1]*2 + DQUOTE_CHAR) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: "ÿÿ"
    """
    if VALID_QUOTED_STRING.match(text) is None:
        raise VCardValueError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_param_value(text):
    """
    param-value, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: Single parameter value

    Examples:
    >>> validate_param_value('')
    >>> validate_param_value(SAFE_CHARS)
    >>> validate_param_value(DQUOTE_CHAR + QSAFE_CHARS[0] + DQUOTE_CHAR)
    >>> validate_param_value(DQUOTE_CHAR + DQUOTE_CHAR) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: ""
    """
    try:
        validate_ptext(text)
    except VCardValueError:
        try:
            validate_quoted_string(text)
        except VCardValueError:
            raise VCardValueError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_text_parameter(parameter):
    """
    text-param, as described on page 35
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param parameter: Single parameter, as returned by get_vcard_property_param

    Examples:
    >>> validate_text_parameter(['VALUE', {'ptext'}])
    """
    param_name = parameter[0].upper()
    param_values = parameter[1]

    if param_name == 'VALUE':
        if param_values != {'ptext'}:
            raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
        return
    elif param_name == 'LANGUAGE':
        if len(param_values) != 1:
            raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
        for param_value in param_values:
            validate_language_tag(param_value)
    else:
        validate_x_name(param_name)
        if len(param_values) != 1:
            raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
        validate_param_value(param_values[0])


def validate_float(text):
    """
    float value, as described on page 10 of RFC 2425
    <http://tools.ietf.org/html/rfc2425#section-5.8.4>

    Examples:
    >>> validate_float('12')
    >>> validate_float('12.345')
    >>> validate_float('+12.345')
    >>> validate_float('-12.345')
    >>> validate_float('12.') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    >>> validate_float('.12') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    >>> validate_float('foo') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    >>> validate_float('++12.345') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    >>> validate_float('--12.345') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    >>> validate_float('12.34.5') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid subvalue ...
    """
    if VALID_FLOAT.match(text) is None:
        raise VCardValueError('{0}, expected float value: {1}'.format(MSG_INVALID_SUBVALUE, text), {})


def validate_uri(text):
    """
    genericurl, as described in RFC 1738
    <http://tools.ietf.org/html/rfc1738#section-5>.
    @param text: Single parameter value

    Examples:
    >>> validate_uri('http://example.org/')
    >>> validate_uri('http\\://example.org/') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid URI ...
    String: http\\://example.org/
    >>> validate_uri('http:') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid URI ...
    String: http:
    """
    parts = urlparse(text)
    if parts[0] == '' or (parts[1] == '' and parts[2] == ''):
        raise VCardValueError(MSG_INVALID_URI, {'String': text})


def validate_vcard_property(prop):
    """
    Checks any property according to
    <http://tools.ietf.org/html/rfc2426#section-3> and
    <http://tools.ietf.org/html/rfc2426#section-4>. Checks are grouped by
    property to allow easy overview rather than a short function.

    @param prop: Formatted property
    """
    property_name = prop['name'].upper()

    try:
        if property_name in ('BEGIN', 'END'):
            # <http://tools.ietf.org/html/rfc2426#section-2.1.1>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            if prop['values'][0][0].lower() != 'vcard':
                raise VCardValueError('{0}: {1} (expected "VCARD")'.format(MSG_INVALID_VALUE, prop['values'][0][0]), {})

        if property_name == 'NAME':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.2>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        if property_name == 'PROFILE':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.3>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            if prop['values'][0][0].lower() != 'vcard':
                raise VCardValueError('{0}: {1} (expected "VCARD")'.format(MSG_INVALID_VALUE, prop['values'][0][0]), {})
            validate_text_value(prop['values'][0][0])

        if property_name == 'SOURCE':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.4>
            _expect_params(prop)
            for param_name, param_values in prop['parameters'].items():
                if param_name.upper() == 'VALUE':
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
                    if 'CONTEXT' in prop['parameters']:
                        raise VCardValueError('{0}: {1} and {2}'.format(MSG_MISMATCH_PARAM, ('VALUE', 'CONTEXT')), {})
                elif param_name.upper() == 'CONTEXT':
                    if param_values != {'word'}:
                        raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
                    if 'VALUE' in prop['parameters']:
                        raise VCardValueError('{0}: {1} and {2}'.format(MSG_MISMATCH_PARAM, ('VALUE', 'CONTEXT')), {})
                else:
                    raise VCardNameError('{0}: {1}'.format(MSG_INVALID_PARAM_NAME, param_name), {})

        if property_name == 'FN':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.1>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'VERSION':
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            if prop['values'][0][0] != '3.0':
                raise VCardValueError('{0}: {1} (expected "3.0")'.format(MSG_INVALID_VALUE, prop['values'][0][0]), {})
        elif property_name == 'N':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.2>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            _expect_value_count(prop['values'], 5)
            # Should names be split?
            for names in prop['values']:
                warnings.showwarning = show_warning
                for name in names:
                    validate_text_value(name)
                    if name.find(SP_CHAR) != -1 and ''.join([''.join(names) for names in prop['values']]) != name:
                        # Space in name
                        # Not just a single name
                        warnings.warn('{0}: {1}'.format(WARN_MULTIPLE_NAMES, name.encode('utf-8')))

        elif property_name == 'NICKNAME':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.3>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            _expect_value_count(prop['values'], 1)

        elif property_name in ['PHOTO', 'LOGO']:
            # <http://tools.ietf.org/html/rfc2426#section-3.1.4>
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            _expect_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            for param_name, param_values in prop['parameters'].items():
                if param_name.upper() == 'ENCODING':
                    if param_values != {'b'}:
                        raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
                    if 'VALUE' in prop['parameters']:
                        raise VCardValueError('{0}: {1} and {2}'.format(MSG_MISMATCH_PARAM, ('ENCODING', 'VALUE')), {})
                elif param_name.upper() == 'TYPE' and 'ENCODING' not in prop['parameters']:
                    raise VCardItemCountError('{0}: {1}'.format(MSG_MISSING_PARAM, 'ENCODING'), {})
                elif param_name.upper() == 'VALUE':
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
                    else:
                        validate_uri(prop['values'][0][0])
                elif param_name.upper() not in ['ENCODING', 'TYPE', 'VALUE']:
                    raise VCardNameError('{0}: {1}'.format(MSG_INVALID_PARAM_NAME, param_name), {})

        elif property_name == 'BDAY':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.5>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_date(prop['values'][0][0])

        elif property_name == 'ADR':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.1>
            _expect_value_count(prop['values'], 7)
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue not in LABEL_TYPE_VALUES:
                                raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_subvalue), {})
                        if param_values == {'intl', 'postal', 'parcel', 'work'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, prop['values']))
                    else:
                        validate_text_parameter(prop)

        elif property_name == 'LABEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.2>
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue not in LABEL_TYPE_VALUES:
                                raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_subvalue), {})
                        if param_values == {'intl', 'postal', 'parcel', 'work'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, prop['values']))
                    else:
                        validate_text_parameter(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'TEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.1>
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue.lower() not in TELEPHONE_TYPE_VALUES:
                                raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_subvalue), {})
                        if set([value.lower() for value in param_values]) == {'voice'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, prop['values']))
                    else:
                        raise VCardNameError('{0}: {1}'.format(MSG_INVALID_PARAM_NAME, param_name), {})
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)

        elif property_name == 'EMAIL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.2>
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue.lower() not in EMAIL_TYPE_VALUES:
                                warnings.warn('{0}: {1}'.format(WARN_INVALID_EMAIL_TYPE, param_subvalue))
                        if set([value.lower() for value in param_values]) == {'internet'}:
                            warnings.warn('{0}: {1[values]}'.format(WARN_DEFAULT_TYPE_VALUE, prop))
                    else:
                        raise VCardNameError('{0}: {1}'.format(MSG_INVALID_PARAM_NAME, param_name), {})
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'MAILER':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.3>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_value_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'TZ':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.1>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            value = prop['values'][0][0]
            validate_time_zone(value)

        elif property_name == 'GEO':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.2>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 2)
            # can the following be...
            #   _expect_subvalue_count(prop['values'][0], 2)
            # ...?
            for value in prop['values']:
                if len(value) != 1:
                    raise VCardItemCountError(
                        '{0}: {1:d} (expected 1)'.format(MSG_INVALID_SUBVALUE_COUNT, len(prop['values'][0])), {})
                validate_float(value[0])

        elif property_name == 'TITLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.1>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'ROLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.2>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            _expect_value_count(prop['values'], 1)
            _expect_subvalue_count(prop['values'][0], 1)
            validate_text_value(prop['values'][0][0])

        elif property_name == 'AGENT':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() != 'VALUE':
                        raise VCardNameError('{0}: {1}'.format(MSG_INVALID_PARAM_NAME, param_values), {})
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(MSG_INVALID_PARAM_VALUE, param_values), {})
                _expect_value_count(prop['values'], 1)
                # can this be...
                #   _expect_subvalue_count(prop['values'][0], 1)
                # ...?
                for value in prop['values']:
                    if len(value) != 1:
                        raise VCardItemCountError(
                            '{0}: {1:d} (expected 1)'.format(MSG_INVALID_SUBVALUE_COUNT, len(prop['values'][0])), {})
                    validate_uri(value[0])
            else:
                # Inline vCard object
                pass  # TODO: Un-escape and validate value

        elif property_name == 'URL':
            # <http://tools.ietf.org/html/rfc2426#section-3.6.8>
            _expect_no_params(prop)
            _expect_value_count(prop['values'], 1)
            validate_uri(prop['values'][0][0])

    except VCardError as error:
        error.context['Property'] = property_name
        err_type = type(error)
        raise err_type(error.message, error.context)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vCard v3.0 (RFC 2426) validating functions

Should contain all the general purpose validation code extracted from
standards.
"""

import re
from urlparse import urlparse
import warnings

# Third party modules
import isodate

# Local modules
from vcard_definitions import \
    DOUBLE_QUOTE_CHARACTER, ID_CHARACTERS, ESCAPED_CHARACTERS, QUOTE_SAFE_CHARACTERS, SAFE_CHARACTERS, SPACE_CHARACTER

from vcard_errors import (
    # Error literals
    NOTE_INVALID_DATE,
    NOTE_INVALID_LANGUAGE_VALUE,
    NOTE_INVALID_PARAMETER_NAME,
    NOTE_INVALID_PARAMETER_VALUE,
    NOTE_INVALID_SUB_VALUE,
    NOTE_INVALID_SUB_VALUE_COUNT,
    NOTE_INVALID_TEXT_VALUE,
    NOTE_INVALID_TIME,
    NOTE_INVALID_TIME_ZONE,
    NOTE_INVALID_URI,
    NOTE_INVALID_VALUE,
    NOTE_INVALID_VALUE_COUNT,
    NOTE_INVALID_X_NAME,
    NOTE_MISMATCH_PARAMETER,
    NOTE_MISSING_PARAMETER,
    NOTE_NON_EMPTY_PARAMETER,
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
VALID_TIMEZONE = re.compile(r'^(Z|[+-]\d{2}:?\d{2})$')
VALID_TIME_WITH_TIMEZONE = re.compile(r'^(\d{2}:?\d{2}:?\d{2}(?:,\d+)?)(.*)$')
VALID_LANGUAGE_TAG = re.compile(r'^([a-z]{1,8})(-[a-z]{1,8})*$')
VALID_X_NAME = re.compile(r'^X-[{0}]+$'.format(re.escape(ID_CHARACTERS)))
VALID_PRESENTATION_TEXT = re.compile(u'^[{0}]*$'.format(re.escape(SAFE_CHARACTERS)))
VALID_TEXT = re.compile(u'^([{0}:{1}]|(\\\\[{2}]))*$'.format(
    re.escape(SAFE_CHARACTERS), DOUBLE_QUOTE_CHARACTER, re.escape(ESCAPED_CHARACTERS)))
VALID_QUOTED_STRING = re.compile(u'^{0}[{1}]{0}$'.format(DOUBLE_QUOTE_CHARACTER, re.escape(QUOTE_SAFE_CHARACTERS)))
VALID_FLOAT = re.compile(r'^[+-]?\d+(\.\d+)?$')

LABEL_TYPE_VALUES = ('dom', 'intl', 'postal', 'parcel', 'home', 'work', 'pref')
TELEPHONE_TYPE_VALUES = (
    'home', 'msg', 'work', 'pref', 'voice', 'fax', 'cell', 'video', 'pager', 'bbs', 'modem', 'car', 'isdn', 'pcs')
EMAIL_TYPE_VALUES = ('internet', 'x400', 'pref', 'dom', 'intl', 'postal', 'parcel', 'home', 'work')


def _expect_no_parameters(property_):
    parameters = __get_parameters(property_)
    if parameters is not None:
        raise VCardItemCountError('{0}: {1}'.format(NOTE_NON_EMPTY_PARAMETER, parameters), {})


def _expect_parameters(property_):
    if __get_parameters(property_) is None:
        raise VCardItemCountError(NOTE_MISSING_PARAMETER, {})


def _expect_value_count(values, count):
    if len(values) != count:
        raise VCardItemCountError('{0}: {1:d} (expected {2})'.format(NOTE_INVALID_VALUE_COUNT, len(values), count), {})


def _expect_sub_value_count(sub_values, count):
    if len(sub_values) != count:
        raise VCardItemCountError(
            '{0}: {1:d} (expected {2})'.format(NOTE_INVALID_SUB_VALUE_COUNT, len(sub_values), count), {})


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
        raise VCardValueError(NOTE_INVALID_DATE, {'String': text})

    try:
        isodate.parse_date(text)
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(NOTE_INVALID_DATE, {'String': text})


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
    if not VALID_TIMEZONE.match(text):
        raise VCardValueError(NOTE_INVALID_TIME_ZONE, {'String': text})

    try:
        isodate.parse_tzinfo(text.replace('+', 'Z+').replace('-', 'Z-'))
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(NOTE_INVALID_TIME_ZONE, {'String': text})


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
    time_timezone = VALID_TIME_WITH_TIMEZONE.match(text)
    if time_timezone is None:
        raise VCardValueError(NOTE_INVALID_TIME, {'String': text})

    time_str, timezone_str = time_timezone.groups()
    try:
        isodate.parse_time(time_str)
    except (isodate.ISO8601Error, ValueError):
        raise VCardValueError(NOTE_INVALID_TIME, {'String': text})

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

    if VALID_LANGUAGE_TAG.match(text) is None:
        raise VCardValueError(NOTE_INVALID_LANGUAGE_VALUE, {'String': text})

    # TODO: Extend to validate according to referenced ISO/RFC standards


def validate_x_name(text):
    """
    @param text: Single parameter name

    Examples:
    >>> validate_x_name('X-abc')
    >>> validate_x_name('X-' + ID_CHARACTERS)
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
        raise VCardNameError(NOTE_INVALID_X_NAME, {'String': text})


def validate_presentation_text(text):
    """
    ptext, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_presentation_text('')
    >>> validate_presentation_text(SAFE_CHARACTERS)
    >>> validate_presentation_text(u'\u000B') #doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: ...
    """
    if VALID_PRESENTATION_TEXT.match(text) is None:
        raise VCardValueError(NOTE_INVALID_PARAMETER_VALUE, {'String': text})


def validate_text_value(text):
    """
    text-value, as described on page 37
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_text_value('')
    >>> validate_text_value('\\\\,')
    >>> validate_text_value(SAFE_CHARACTERS)
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
        raise VCardValueError(NOTE_INVALID_TEXT_VALUE, {'String': text})


def validate_quoted_string(text):
    """
    quoted-string, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_quoted_string(DOUBLE_QUOTE_CHARACTER + QUOTE_SAFE_CHARACTERS[0] + DOUBLE_QUOTE_CHARACTER)
    >>> validate_quoted_string(DOUBLE_QUOTE_CHARACTER + DOUBLE_QUOTE_CHARACTER) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    >>> validate_quoted_string(
    ... DOUBLE_QUOTE_CHARACTER + QUOTE_SAFE_CHARACTERS[-1]*2 + DOUBLE_QUOTE_CHARACTER) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: "ÿÿ"
    """
    if VALID_QUOTED_STRING.match(text) is None:
        raise VCardValueError(NOTE_INVALID_PARAMETER_VALUE, {'String': text})


def validate_param_value(text):
    """
    param-value, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: Single parameter value

    Examples:
    >>> validate_param_value('')
    >>> validate_param_value(SAFE_CHARACTERS)
    >>> validate_param_value(DOUBLE_QUOTE_CHARACTER + QUOTE_SAFE_CHARACTERS[0] + DOUBLE_QUOTE_CHARACTER)
    >>> validate_param_value(DOUBLE_QUOTE_CHARACTER + DOUBLE_QUOTE_CHARACTER) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    VCardValueError: Invalid parameter value ...
    String: ""
    """
    try:
        validate_presentation_text(text)
    except VCardValueError:
        try:
            validate_quoted_string(text)
        except VCardValueError:
            raise VCardValueError(NOTE_INVALID_PARAMETER_VALUE, {'String': text})


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
            raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
        return
    elif param_name == 'LANGUAGE':
        if len(param_values) != 1:
            raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
        for param_value in param_values:
            validate_language_tag(param_value)
    else:
        validate_x_name(param_name)
        if len(param_values) != 1:
            raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
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
    VCardValueError: Invalid sub-value ...
    >>> validate_float('.12') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid sub-value ...
    >>> validate_float('foo') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid sub-value ...
    >>> validate_float('++12.345') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid sub-value ...
    >>> validate_float('--12.345') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid sub-value ...
    >>> validate_float('12.34.5') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    VCardValueError: Invalid sub-value ...
    """
    if VALID_FLOAT.match(text) is None:
        raise VCardValueError('{0}, expected float value: {1}'.format(NOTE_INVALID_SUB_VALUE, text), {})


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
        raise VCardValueError(NOTE_INVALID_URI, {'String': text})


def validate_vcard_property(property_):
    """
    Checks any property according to
    <http://tools.ietf.org/html/rfc2426#section-3> and
    <http://tools.ietf.org/html/rfc2426#section-4>. Checks are grouped by
    property to allow easy overview rather than a short function.

    @param property_: Formatted property
    """
    property_name = property_.name.upper()

    try:
        if property_name in ('BEGIN', 'END'):
            # <http://tools.ietf.org/html/rfc2426#section-2.1.1>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            if property_.values[0][0].lower() != 'vcard':
                raise VCardValueError(
                    '{0}: {1} (expected "VCARD")'.format(NOTE_INVALID_VALUE, property_.values[0][0]), {})

        if property_name == 'NAME':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.2>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        if property_name == 'PROFILE':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.3>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            if property_.values[0][0].lower() != 'vcard':
                raise VCardValueError(
                    '{0}: {1} (expected "VCARD")'.format(NOTE_INVALID_VALUE, property_.values[0][0]), {})
            validate_text_value(property_.values[0][0])

        if property_name == 'SOURCE':
            # <http://tools.ietf.org/html/rfc2426#section-2.1.4>
            _expect_parameters(property_)
            for parameter_name, param_values in property_.parameters.items():
                if parameter_name.upper() == 'VALUE':
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
                    if 'CONTEXT' in property_.parameters:
                        raise VCardValueError(
                            '{0}: {1} and {2}'.format(NOTE_MISMATCH_PARAMETER, ('VALUE', 'CONTEXT')), {})
                elif parameter_name.upper() == 'CONTEXT':
                    if param_values != {'word'}:
                        raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
                    if 'VALUE' in property_.parameters:
                        raise VCardValueError(
                            '{0}: {1} and {2}'.format(NOTE_MISMATCH_PARAMETER, ('VALUE', 'CONTEXT')), {})
                else:
                    raise VCardNameError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_NAME, parameter_name), {})

        if property_name == 'FN':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.1>
            if property_.parameters is not None:
                for parameter in property_.parameters.items():
                    validate_text_parameter(parameter)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'VERSION':
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            if property_.values[0][0] != '3.0':
                raise VCardValueError(
                    '{0}: {1} (expected "3.0")'.format(NOTE_INVALID_VALUE, property_.values[0][0]), {})
        elif property_name == 'N':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.2>
            if property_.parameters is not None:
                for parameter in property_.parameters.items():
                    validate_text_parameter(parameter)
            _expect_value_count(property_.values, 5)
            # Should names be split?
            for names in property_.values:
                warnings.showwarning = show_warning
                for name in names:
                    validate_text_value(name)
                    if name.find(SPACE_CHARACTER) != -1 and \
                            ''.join([''.join(names) for names in property_.values]) != name:
                        # Space in name
                        # Not just a single name
                        warnings.warn('{0}: {1}'.format(WARN_MULTIPLE_NAMES, name.encode('utf-8')))

        elif property_name == 'NICKNAME':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.3>
            if property_.parameters is not None:
                for parameter in property_.parameters.items():
                    validate_text_parameter(parameter)
            _expect_value_count(property_.values, 1)

        elif property_name in ['PHOTO', 'LOGO']:
            # <http://tools.ietf.org/html/rfc2426#section-3.1.4>
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            _expect_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            for parameter_name, param_values in property_.parameters.items():
                if parameter_name.upper() == 'ENCODING':
                    if param_values != {'b'}:
                        raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
                    if 'VALUE' in property_.parameters:
                        raise VCardValueError(
                            '{0}: {1} and {2}'.format(NOTE_MISMATCH_PARAMETER, ('ENCODING', 'VALUE')), {})
                elif parameter_name.upper() == 'TYPE' and 'ENCODING' not in property_.parameters:
                    raise VCardItemCountError('{0}: {1}'.format(NOTE_MISSING_PARAMETER, 'ENCODING'), {})
                elif parameter_name.upper() == 'VALUE':
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
                    else:
                        validate_uri(property_.values[0][0])
                elif parameter_name.upper() not in ['ENCODING', 'TYPE', 'VALUE']:
                    raise VCardNameError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_NAME, parameter_name), {})

        elif property_name == 'BDAY':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.5>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_date(property_.values[0][0])

        elif property_name == 'ADR':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.1>
            _expect_value_count(property_.values, 7)
            if property_.parameters is not None:
                for parameter_name, param_values in property_.parameters.items():
                    if parameter_name.upper() == 'TYPE':
                        for param_sub_value in param_values:
                            if param_sub_value not in LABEL_TYPE_VALUES:
                                raise VCardValueError(
                                    '{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_sub_value), {})
                        if param_values == {'intl', 'postal', 'parcel', 'work'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, property_.values))
                    else:
                        validate_text_parameter(property_)

        elif property_name == 'LABEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.2>
            if property_.parameters is not None:
                for parameter_name, param_values in property_.parameters.items():
                    if parameter_name.upper() == 'TYPE':
                        for param_sub_value in param_values:
                            if param_sub_value not in LABEL_TYPE_VALUES:
                                raise VCardValueError(
                                    '{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_sub_value), {})
                        if param_values == {'intl', 'postal', 'parcel', 'work'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, property_.values))
                    else:
                        validate_text_parameter(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'TEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.1>
            if property_.parameters is not None:
                for parameter_name, param_values in property_.parameters.items():
                    if parameter_name.upper() == 'TYPE':
                        for param_sub_value in param_values:
                            if param_sub_value.lower() not in TELEPHONE_TYPE_VALUES:
                                raise VCardValueError(
                                    '{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_sub_value), {})
                        if set([value.lower() for value in param_values]) == {'voice'}:
                            warnings.warn('{0}: {1}'.format(WARN_DEFAULT_TYPE_VALUE, property_.values))
                    else:
                        raise VCardNameError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_NAME, parameter_name), {})
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)

        elif property_name == 'EMAIL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.2>
            if property_.parameters is not None:
                for parameter_name, param_values in property_.parameters.items():
                    if parameter_name.upper() == 'TYPE':
                        for param_sub_value in param_values:
                            if param_sub_value.lower() not in EMAIL_TYPE_VALUES:
                                warnings.warn('{0}: {1}'.format(WARN_INVALID_EMAIL_TYPE, param_sub_value))
                        if set([value.lower() for value in param_values]) == {'internet'}:
                            warnings.warn('{0}: {1[values]}'.format(WARN_DEFAULT_TYPE_VALUE, property_))
                    else:
                        raise VCardNameError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_NAME, parameter_name), {})
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'MAILER':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.3>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'TZ':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.1>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            value = property_.values[0][0]
            validate_time_zone(value)

        elif property_name == 'GEO':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.2>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 2)
            # can the following be...
            #   _expect_sub_value_count(property_.values[0], 2)
            # ...?
            for value in property_.values:
                if len(value) != 1:
                    raise VCardItemCountError(
                        '{0}: {1:d} (expected 1)'.format(NOTE_INVALID_SUB_VALUE_COUNT, len(property_.values[0])), {})
                validate_float(value[0])

        elif property_name == 'TITLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.1>
            if property_.parameters is not None:
                for parameter in property_.parameters.items():
                    validate_text_parameter(parameter)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'ROLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.2>
            if property_.parameters is not None:
                for parameter in property_.parameters.items():
                    validate_text_parameter(parameter)
            _expect_value_count(property_.values, 1)
            _expect_sub_value_count(property_.values[0], 1)
            validate_text_value(property_.values[0][0])

        elif property_name == 'AGENT':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            if property_.parameters is not None:
                for parameter_name, param_values in property_.parameters.items():
                    if parameter_name.upper() != 'VALUE':
                        raise VCardNameError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_NAME, param_values), {})
                    if param_values != {'uri'}:
                        raise VCardValueError('{0}: {1}'.format(NOTE_INVALID_PARAMETER_VALUE, param_values), {})
                _expect_value_count(property_.values, 1)
                # can this be...
                #   _expect_sub_value_count(property_.values[0], 1)
                # ...?
                for value in property_.values:
                    if len(value) != 1:
                        raise VCardItemCountError(
                            '{0}: {1:d} (expected 1)'.format(
                                NOTE_INVALID_SUB_VALUE_COUNT, len(property_.values[0])), {})
                    validate_uri(value[0])
            else:
                # Inline vCard object
                pass  # TODO: Un-escape and validate value

        elif property_name == 'URL':
            # <http://tools.ietf.org/html/rfc2426#section-3.6.8>
            _expect_no_parameters(property_)
            _expect_value_count(property_.values, 1)
            validate_uri(property_.values[0][0])

    except VCardError as error:
        error.context['Property'] = property_name
        err_type = type(error)
        raise err_type(error.message, error.context)


def __get_parameters(property_):
    return property_.parameters

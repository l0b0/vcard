#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vCards v3.0 (RFC 2426) validating functions

Should contain all the general purpose validation code extracted from
standards.
"""

import re
import sys
from urlparse import urlparse
import warnings

# Third party modules
import isodate

# Local modules
from vcard_defs import DQUOTE_CHAR, \
    ID_CHARS, \
    MSG_INVALID_DATE, \
    MSG_INVALID_LANGUAGE_VALUE, \
    MSG_INVALID_PARAM_NAME, \
    MSG_INVALID_PARAM_VALUE, \
    MSG_INVALID_SUBVALUE, \
    MSG_INVALID_SUBVALUE_COUNT, \
    MSG_INVALID_TIME, \
    MSG_INVALID_TIME_ZONE, \
    MSG_INVALID_URI, \
    MSG_INVALID_VALUE_COUNT, \
    MSG_INVALID_X_NAME, \
    MSG_MISMATCH_PARAM, \
    MSG_MISSING_PARAM, \
    MSG_NON_EMPTY_PARAM, \
    QSAFE_CHARS, \
    SAFE_CHARS, \
    SP_CHAR, \
    WARN_DEFAULT_TYPE_VALUE, \
    WARN_INVALID_EMAIL_TYPE, \
    WARN_MULTIPLE_NAMES
    

# pylint: disable-msg=R0913,W0613,W0622
def _show_warning(
    message,
    category = UserWarning,
    filename = '',
    lineno = -1,
    file = sys.stderr,
    line = None):
    """Custom simple warning."""
    file.write(str(message) + '\n')
# pylint: enable-msg=R0913,W0613,W0622


def _stringify(text):
    """
    Get the text as a string representation
    
    @param text: Something convertible to str
    @return: Printable string
    """
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    if not isinstance(text, str):
        text = str(text)
    return text


class VCardFormatError(Exception):
    """Thrown if the text given is not a valid according to RFC 2426."""
    def __init__(self, message, context):
        """
        vCard format error.

        @param message: Error message
        @param context: Dictionary with context information

        Examples:
        >>> raise VCardFormatError('test', {})
        Traceback (most recent call last):
        VCardFormatError: test
        >>> raise VCardFormatError('with path', {'File': '/home/user/test.vcf'})
        Traceback (most recent call last):
        VCardFormatError: with path
        File: /home/user/test.vcf
        >>> raise VCardFormatError('Error with lots of context', {
        ... 'File': '/home/user/test.vcf',
        ... 'File line': 120,
        ... 'vCard line': 5,
        ... 'Property': 'ADR',
        ... 'Property line': 2,
        ... 'String': 'too;few;values;êéè'})
        Traceback (most recent call last):
        VCardFormatError: Error with lots of context
        File: /home/user/test.vcf
        File line: 120
        vCard line: 5
        Property: ADR
        Property line: 2
        String: too;few;values;êéè
        >>> try:
        ...     raise VCardFormatError('test', {'Property': 'ADR'})
        ... except VCardFormatError as error:
        ...     error.context['File'] = '/home/user/test.vcf'
        ...     raise VCardFormatError(error.message, error.context)
        Traceback (most recent call last):
        VCardFormatError: test
        File: /home/user/test.vcf
        Property: ADR
        >>> raise VCardFormatError('Cöntexte randomisé', {'foo': QSAFE_CHARS[-1]*2})
        Traceback (most recent call last):
        VCardFormatError: Cöntexte randomisé
        foo: ÿÿ
        """
        Exception.__init__(self)
        self.message = message
        self.context = context


    def __str__(self):
        """
        Outputs error with ordered context info.
        
        @return: Printable error message
        """
        message = self.message

        # Sort context information
        keys = [
            'File',
            'File line',
            'vCard line',
            'Property',
            'Property line',
            'String']
        for key in keys:
            if key in self.context:
                message += '\n' + _stringify(key) + ': ' + \
                _stringify(self.context.pop(key))
        
        # Output other context strings any old way
        for key in self.context.keys():
            message += '\n' + _stringify(key) + ': ' + \
            _stringify(self.context.pop(key))

        return message


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
    VCardFormatError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 2000:01:01
    >>> validate_date('2000101') # Too short
    Traceback (most recent call last):
    VCardFormatError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 2000101
    >>> validate_date('20080229')
    >>> validate_date('20100229') # Not a leap year
    Traceback (most recent call last):
    VCardFormatError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 20100229
    >>> validate_date('19000229') # Not a leap year (divisible by 100)
    Traceback (most recent call last):
    VCardFormatError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: 19000229
    >>> validate_date('20000229') # Leap year (divisible by 400)
    >>> validate_date('aaaa-bb-cc')
    Traceback (most recent call last):
    VCardFormatError: Invalid date (See RFC 2425 section 5.8.4 for date syntax)
    String: aaaa-bb-cc
    """
    if re.match(r'^\d{4}-?\d{2}-?\d{2}$', text) is None:
        raise VCardFormatError(MSG_INVALID_DATE, {'String': text})

    try:
        isodate.parse_date(text)
    except (isodate.ISO8601Error, ValueError):
        raise VCardFormatError(MSG_INVALID_DATE, {'String': text})


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
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: Z+01:00
    >>> validate_time_zone('+1:00') # Need preceding zero
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: +1:00
    >>> validate_time_zone('0100') # Need + or -
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: 0100
    >>> validate_time_zone('01') # Need colon and minutes
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: 01
    >>> validate_time_zone('01:') # Need minutes
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: 01:
    >>> validate_time_zone('01:1') # Need preceding zero
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: 01:1
    """
    if not re.match(r'^(Z|[+-]\d{2}:?\d{2})$', text):
        raise VCardFormatError(MSG_INVALID_TIME_ZONE, {'String': text})

    try:
        isodate.parse_tzinfo(text.replace('+', 'Z+').replace('-', 'Z-'))
    except (isodate.ISO8601Error, ValueError):
        raise VCardFormatError(MSG_INVALID_TIME_ZONE, {'String': text})


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
    VCardFormatError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 01:02:60
    >>> validate_time('01:60:59')
    Traceback (most recent call last):
    VCardFormatError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 01:60:59
    >>> validate_time('24:00:00')
    Traceback (most recent call last):
    VCardFormatError: Invalid time (See RFC 2425 section 5.8.4 for time syntax)
    String: 24:00:00
    >>> validate_time('00:00:00Z+01')
    Traceback (most recent call last):
    VCardFormatError: Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)
    String: Z+01
    """
    time_timezone = re.match(r'^(\d{2}:?\d{2}:?\d{2}(?:,\d+)?)(.*)$', text)
    if time_timezone is None:
        raise VCardFormatError(MSG_INVALID_TIME, {'String': text})

    time_str, timezone_str = time_timezone.groups()
    try:
        isodate.parse_time(time_str)
    except (isodate.ISO8601Error, ValueError):
        raise VCardFormatError(MSG_INVALID_TIME, {'String': text})

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
    VCardFormatError: Invalid language (See RFC 1766 section 2 for details)
    String: -us
    >>> validate_language_tag('en-') # Can't end with dash
    Traceback (most recent call last):
    VCardFormatError: Invalid language (See RFC 1766 section 2 for details)
    String: en-
    >>> validate_language_tag('en-US')

    """
    text = text.lower() # Case insensitive

    if re.match(r'^([a-z]{1,8})(-[a-z]{1,8})*$', text) is None:
        raise VCardFormatError(MSG_INVALID_LANGUAGE_VALUE, {'String': text})

    # TODO: Extend to validate according to referenced ISO/RFC standards


def validate_x_name(text):
    """
    @param text: Single parameter name

    Examples:
    >>> validate_x_name('X-abc')
    >>> validate_x_name('X-' + ID_CHARS)
    >>> validate_x_name('X-') # Have to have more characters
    Traceback (most recent call last):
    VCardFormatError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: X-
    >>> validate_x_name('') # Have to start with X-
    Traceback (most recent call last):
    VCardFormatError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: 
    >>> validate_x_name('x-abc') # X must be upper case
    Traceback (most recent call last):
    VCardFormatError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: x-abc
    >>> validate_x_name('foo') # Have to start with X-
    Traceback (most recent call last):
    VCardFormatError: Invalid X-name (See RFC 2426 section 4 for x-name syntax)
    String: foo
    """
    if re.match(r'^X-[' + ID_CHARS + ']+$', text) is None:
        raise VCardFormatError(MSG_INVALID_X_NAME, {'String': text})


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
    VCardFormatError: Invalid parameter value (See RFC 2426 section 4 for param-value syntax)
    String: ...
    """
    if re.match('^[' + SAFE_CHARS + ']*$', text) is None:
        raise VCardFormatError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_quoted_string(text):
    """
    quoted-string, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: String

    Examples:
    >>> validate_quoted_string(DQUOTE_CHAR + QSAFE_CHARS[0] + DQUOTE_CHAR)
    >>> validate_quoted_string(DQUOTE_CHAR + DQUOTE_CHAR)
    Traceback (most recent call last):
    VCardFormatError: Invalid parameter value (See RFC 2426 section 4 for param-value syntax)
    String: ""
    >>> validate_quoted_string(DQUOTE_CHAR + QSAFE_CHARS[-1]*2 + DQUOTE_CHAR)
    Traceback (most recent call last):
    VCardFormatError: Invalid parameter value (See RFC 2426 section 4 for param-value syntax)
    String: "ÿÿ"
    """
    if re.match(
        r'^' + DQUOTE_CHAR + '[' + QSAFE_CHARS + ']' + DQUOTE_CHAR + '$',
        text) is None:
        raise VCardFormatError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_param_value(text):
    """
    param-value, as described on page 28
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param text: Single parameter value
    
    Examples:
    >>> validate_param_value('')
    >>> validate_param_value(SAFE_CHARS)
    >>> validate_param_value(DQUOTE_CHAR + QSAFE_CHARS[0] + DQUOTE_CHAR)
    >>> validate_param_value(DQUOTE_CHAR + DQUOTE_CHAR)
    Traceback (most recent call last):
    VCardFormatError: Invalid parameter value (See RFC 2426 section 4 for param-value syntax)
    String: ""
    """
    try:
        validate_ptext(text)
    except VCardFormatError:
        try:
            validate_quoted_string(text)
        except VCardFormatError:
            raise VCardFormatError(MSG_INVALID_PARAM_VALUE, {'String': text})


def validate_text_parameter(parameter):
    """
    text-param, as described on page 35
    <http://tools.ietf.org/html/rfc2426#section-4>

    @param parameter: Single parameter, as returned by get_vcard_property_param
    
    Examples:
    >>> validate_text_parameter(['VALUE', set(['ptext'])])
    """
    param_name = parameter[0].upper()
    param_values = parameter[1]

    if param_name == 'VALUE':
        if param_values != set(['ptext']):
            raise VCardFormatError(
                MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                {})
        return
    elif param_name == 'LANGUAGE':
        if len(param_values) != 1:
            raise VCardFormatError(
                MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                {})
        validate_language_tag(param_values[0])
    else:
        validate_x_name(param_name)
        if len(param_values) != 1:
            raise VCardFormatError(
                MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                {})
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
    >>> validate_float('12.')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: 12.
    >>> validate_float('.12')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: .12
    >>> validate_float('foo')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: foo
    >>> validate_float('++12.345')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: ++12.345
    >>> validate_float('--12.345')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: --12.345
    >>> validate_float('12.34.5')
    Traceback (most recent call last):
    VCardFormatError: Invalid subvalue (See RFC 2426 section 3 for details), expected float value: 12.34.5
    """
    if re.match(r'^[+-]?\d+(\.\d+)?$', text) is None:
        raise VCardFormatError(
            MSG_INVALID_SUBVALUE + ', expected float value: %s' % text,
            {})


def validate_uri(text):
    """
    genericurl, as described in RFC 1738 <http://tools.ietf.org/html/rfc1738#section-5>.
    @param text: Single parameter value

    Examples:
    >>> validate_uri('http://example.org/')
    >>> validate_uri('http\\://example.org/')
    Traceback (most recent call last):
    VCardFormatError: Invalid URI (See RFC 1738 section 5 for genericurl syntax)
    String: http\\://example.org/
    >>> validate_uri('http:')
    Traceback (most recent call last):
    VCardFormatError: Invalid URI (See RFC 1738 section 5 for genericurl syntax)
    String: http:
    """
    parts = urlparse(text)
    if parts[0] == '' or (parts[1] == '' and parts[2] == ''):
        raise VCardFormatError(MSG_INVALID_URI, {'String': text})


def validate_vcard_property(prop):
    """
    Checks any property according to
    <http://tools.ietf.org/html/rfc2426#section-3> and
    <http://tools.ietf.org/html/rfc2426#section-4>. Checks are grouped by
    property to allow easy overview rather than a short function.

    @param property: Formatted property
    """
    property_name = prop['name'].upper()

    try:
        if property_name == 'FN':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.1>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})

        elif property_name == 'N':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.2>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            if len(prop['values']) != 5:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 5)' % len(
                        prop['values']),
                    {})
            # Should names be split?
            for names in prop['values']:
                warnings.showwarning = _show_warning
                for name in names:
                    if name.find(SP_CHAR) != -1 and \
                           ''.join([''.join(names) \
                                    for names in prop['values']]) != name:
                        # Space in name
                        # Not just a single name
                        warnings.warn(
                            WARN_MULTIPLE_NAMES + ': %s' % name.encode('utf-8'))

        elif property_name == 'NICKNAME':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.3>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})

        elif property_name in ['PHOTO', 'LOGO']:
            # <http://tools.ietf.org/html/rfc2426#section-3.1.4>
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            if not 'parameters' in prop:
                raise VCardFormatError(MSG_MISSING_PARAM, {})
            for param_name, param_values in prop['parameters'].items():
                if param_name.upper() == 'ENCODING':
                    if param_values != set(['b']):
                        raise VCardFormatError(
                            MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                            {})
                    if 'VALUE' in prop['parameters']:
                        raise VCardFormatError(
                            MSG_MISMATCH_PARAM  + ': %s and %s' % (
                                'ENCODING',
                                'VALUE'),
                            {})
                elif param_name.upper() == 'TYPE' and \
                       'ENCODING' not in prop['parameters']:
                    raise VCardFormatError(
                        MSG_MISSING_PARAM + ': %s' % 'ENCODING',
                        {})
                elif param_name.upper() == 'VALUE' and \
                     param_values != set(['uri']):
                    raise VCardFormatError(
                        MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                        {})
                elif param_name.upper() not in ['ENCODING', 'TYPE', 'VALUE']:
                    raise VCardFormatError(
                        MSG_INVALID_PARAM_NAME + ': %s' % param_name,
                        {})
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if len(prop['values'][0]) != 1:
                raise VCardFormatError(
                    MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values'][0]),
                    {})
            validate_uri(prop['values'][0][0])


        elif property_name == 'BDAY':
            # <http://tools.ietf.org/html/rfc2426#section-3.1.5>
            if 'parameters' in prop:
                raise VCardFormatError(
                    MSG_NON_EMPTY_PARAM + ': %s' % prop['parameters'],
                    {})
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if len(prop['values'][0]) != 1:
                raise VCardFormatError(
                    MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values'][0]),
                    {})
            validate_date(prop['values'][0][0])

        elif property_name == 'ADR':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.1>
            if len(prop['values']) != 7:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 7)' % len(
                        prop['values']),
                    {})
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue not in [
                                'dom',
                                'intl',
                                'postal',
                                'parcel',
                                'home',
                                'work',
                                'pref']:
                                raise VCardFormatError(
                                    MSG_INVALID_PARAM_VALUE + \
                                    ': %s' % param_subvalue,
                                    {})
                        if param_values == set([
                            'intl',
                            'postal',
                            'parcel',
                            'work']):
                            warnings.warn(
                                WARN_DEFAULT_TYPE_VALUE + \
                                ': %s' % prop['values'])
                    else:
                        validate_text_parameter(parameter)

        elif property_name == 'LABEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.2.2>
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue not in [
                                'dom',
                                'intl',
                                'postal',
                                'parcel',
                                'home',
                                'work',
                                'pref']:
                                raise VCardFormatError(
                                    MSG_INVALID_PARAM_VALUE + ': %s' % \
                                    param_subvalue,
                                    {})
                        if param_values == set([
                            'intl',
                            'postal',
                            'parcel',
                            'work']):
                            warnings.warn(
                                WARN_DEFAULT_TYPE_VALUE + ': %s' % \
                                prop['values'])
                    else:
                        validate_text_parameter(parameter)

        elif property_name == 'TEL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.1>
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue.lower() not in [
                                'home',
                                'msg',
                                'work',
                                'pref',
                                'voice',
                                'fax',
                                'cell',
                                'video',
                                'pager',
                                'bbs',
                                'modem',
                                'car',
                                'isdn',
                                'pcs']:
                                raise VCardFormatError(
                                    MSG_INVALID_PARAM_VALUE + \
                                    ': %s' % param_subvalue,
                                    {})
                        if set([value.lower() for value in param_values]) == \
                               set(['voice']):
                            warnings.warn(
                                WARN_DEFAULT_TYPE_VALUE + ': %s' % \
                                prop['values'])
                    else:
                        raise VCardFormatError(
                            MSG_INVALID_PARAM_NAME + ': %s' % param_name,
                            {})

        elif property_name == 'EMAIL':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.2>
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() == 'TYPE':
                        for param_subvalue in param_values:
                            if param_subvalue.lower() not in [
                                'internet',
                                'x400',
                                'pref',
                                'dom', # IANA registered address types?
                                'intl',
                                'postal',
                                'parcel',
                                'home',
                                'work']:
                                warnings.warn(
                                    WARN_INVALID_EMAIL_TYPE + \
                                    ': %s' % param_subvalue)
                        if set([value.lower() for value in param_values]) == \
                               set(['internet']):
                            warnings.warn(
                                WARN_DEFAULT_TYPE_VALUE + ': %s' % \
                                prop['values'])
                    else:
                        raise VCardFormatError(
                            MSG_INVALID_PARAM_NAME + ': %s' % param_name,
                            {})

        elif property_name == 'MAILER':
            # <http://tools.ietf.org/html/rfc2426#section-3.3.3>
            if 'parameters' in prop:
                raise VCardFormatError(
                    MSG_NON_EMPTY_PARAM + ': %s' % prop['parameters'],
                    {})
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})

        elif property_name == 'TZ':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.1>
            if 'parameters' in prop:
                raise VCardFormatError(
                    MSG_NON_EMPTY_PARAM + ': %s' % prop['parameters'],
                    {})
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            if len(prop['values'][0]) != 1:
                raise VCardFormatError(
                    MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values'][0]),
                    {})
            value = prop['values'][0][0]
            validate_time_zone(value)

        elif property_name == 'GEO':
            # <http://tools.ietf.org/html/rfc2426#section-3.4.2>
            if 'parameters' in prop:
                raise VCardFormatError(
                    MSG_NON_EMPTY_PARAM + ': %s' % prop['parameters'],
                    {})
            if len(prop['values']) != 2:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 2)' % len(
                        prop['values']),
                    {})
            for value in prop['values']:
                if len(value) != 1:
                    raise VCardFormatError(
                        MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                            prop['values'][0]),
                        {})
                validate_float(value[0])

        elif property_name == 'TITLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.1>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            for value in prop['values']:
                if len(value) != 1:
                    raise VCardFormatError(
                        MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                            prop['values'][0]),
                        {})

        elif property_name == 'ROLE':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.2>
            if 'parameters' in prop:
                for parameter in prop['parameters'].items():
                    validate_text_parameter(parameter)
            if len(prop['values']) != 1:
                raise VCardFormatError(
                    MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                        prop['values']),
                    {})
            for value in prop['values']:
                if len(value) != 1:
                    raise VCardFormatError(
                        MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' % len(
                            prop['values'][0]),
                        {})

        elif property_name == 'AGENT':
            # <http://tools.ietf.org/html/rfc2426#section-3.5.4>
            if 'parameters' in prop:
                for param_name, param_values in prop['parameters'].items():
                    if param_name.upper() != 'VALUE':
                        raise VCardFormatError(
                            MSG_INVALID_PARAM_NAME + ': %s' % param_values,
                            {})
                    if param_values != set(['uri']):
                        raise VCardFormatError(
                            MSG_INVALID_PARAM_VALUE + ': %s' % param_values,
                            {})
                if len(prop['values']) != 1:
                    raise VCardFormatError(
                        MSG_INVALID_VALUE_COUNT + ': %d (expected 1)' % len(
                            prop['values']),
                        {})
                for value in prop['values']:
                    if len(value) != 1:
                        raise VCardFormatError(
                            MSG_INVALID_SUBVALUE_COUNT + ': %d (expected 1)' \
                            % len(
                                prop['values'][0]),
                            {})
                    validate_uri(value[0])
            else:
                # Inline vCard object
                pass # TODO: Un-escape and validate value

    except VCardFormatError as error:
        error.context['Property'] = property_name
        raise VCardFormatError(error.message, error.context)
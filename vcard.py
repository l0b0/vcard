#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""vCards v3.0 (RFC 2426) class and parsing + validating functions"""

__author__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__url__ = 'http://vcard-module.sourceforge.net/'
__copyright__ = 'Copyright (C) 2009 Victor Engmark'
__license__ = 'GPLv3'

import re
import warnings

# Literals, RFC 2426 pages 27, 28
ALPHA_CHARS = u'\u0041-\u005A\u0061-\u007A'
CHAR_CHARS = u'\u0001-\u007F'
CR_CHARS = u'\u000D'
LF_CHARS = u'\u000A'
CRLF_CHARS = CR_CHARS + LF_CHARS
CTL_CHARS = u'\u0000-\u001F\u007F'
DIGIT_CHARS = u'\u0030-\u0039'
DQUOTE_CHARS = u'\u0022'
HTAB_CHARS = u'\u0009'
SP_CHARS = u'\u0020'
VCHAR_CHARS = u'\u0021-\u007E'
WSP_CHARS = SP_CHARS + HTAB_CHARS
NON_ASCII_CHARS = u'\u0080-\u00FF'
QSAFE_CHARS = WSP_CHARS + u'\u0021' + u'\u0023-\u007E' + NON_ASCII_CHARS
SAFE_CHARS = WSP_CHARS + u'\u0021' + u'\u0023-\u002B' + u'\u002D-\u0039' + \
             u'\u003C-\u007E' + NON_ASCII_CHARS
VALUE_CHARS = WSP_CHARS + VCHAR_CHARS + NON_ASCII_CHARS

# Known property names (RFC 2426 page 4)
MANDATORY_PROPERTIES = ['FN', 'N', 'VERSION']
PREDEFINED_PROPERTIES = ['BEGIN', 'END', 'NAME', 'PROFILE', 'SOURCE']
OTHER_PROPERTIES = [
    'ADR', 'AGENT', 'BDAY', 'CATEGORIES', 'CLASS', 'EMAIL', 'GEO', 'KEY',
    'LABEL', 'LOGO', 'MAILER', 'NICKNAME', 'NOTE', 'ORG', 'PHOTO', 'PRODID',
    'REV', 'ROLE', 'SORT-STRING', 'SOUND', 'TEL', 'TITLE', 'TZ', 'UID', 'URL']
ALL_PROPERTIES = MANDATORY_PROPERTIES + PREDEFINED_PROPERTIES + OTHER_PROPERTIES

# IDs for group, name, iana-token, x-name, param-name (RFC 2426 page 29)
ID_CHARS = ALPHA_CHARS + DIGIT_CHARS + '-'

VCARD_LINE_MAX_LENGTH = 75 # RFC 2426 page 6

# Error literals
MSG_CONTINUATION_AT_START = 'Continuation line at start of vCard'
MSG_DOT_AT_LINE_START = 'Dot at start of line without group name'
MSG_MISSING_GROUP = 'Missing group'
MSG_MISMATCH_GROUP = 'Group mismatch'
MSG_INVALID_FIRST_LINE = 'Invalid first line'
MSG_INVALID_LAST_LINE = 'Invalid last line'
MSG_INVALID_VALUE = 'Invalid value'
MSG_INVALID_PARAM_NAME = 'Invalid parameter name'
MSG_INVALID_SUBVALUE = 'Invalid subvalue'
MSG_EMPTY_LINE = 'Empty line found'
MSG_VALUE_STRING_MISSING = 'Missing value string'
MSG_INVALID_PROPERTY_NAME = 'Invalid property name'
MSG_MISSING_PROPERTY = 'Mandatory property missing'
MSG_EMPTY_VCARD = 'vCard is empty'
MSG_INVALID_LINE_SEPARATOR = 'Invalid line ending; should be CRLF (\\r\\n)'

class VCardFormatError(Exception):
    """Thrown by VCard if the text given is not a valid according to vCard 3.0"""
    def __init__(self, message, line_number = None, property_name = None):
        """
        vCard format error
        @param message: Error message
        @param property_name: Property of the line (if applicable)
        @param line_number: Line in the vCard where the error happened (if
        applicable)
        """
        Exception.__init__(self)
        self.message = message
        self.line_number = line_number
        self.property_name = property_name

    def __str__(self):
        msg = 'vCard format error: %s' % self.message
        if self.line_number is not None:
            msg += '\nLine number: %i' % self.line_number
        if self.property_name is not None:
            msg += '\nProperty: %s' % self.property_name
        return msg

def find_unescaped(text, char, escape_char = '\\'):
    """
    Find occurrence of an unescaped character
    @param text: String
    @param char: Character to find
    @param escape_char: Escape character
    @return: Index of first match, None if no match
    """
    unescaped_regex = '(?<!' + escape_char + ')' + \
            '(?:' + escape_char + escape_char + ')*' + \
            '(' + char + ')'
    regex = re.compile(unescaped_regex)

    char_match = regex.search(text)

    if char_match is None:
        return None
    return char_match.start(1)

def split_unescaped(text, separator, escape_char = '\\\\'):
    """
    Find strings separated by an unescaped character
    @param text: String
    @param separator: Separator
    @param escape_char: Escape character
    @return: List of strings between separators, excluding the separator
    """
    result = []
    while True:
        index = find_unescaped(text, separator, escape_char)
        if index is not None:
            result.append(text[:index])
            text = text[index + 1:]
        else:
            result.append(text)
            return result

def unfold_vcard_lines(lines):
    """
    Unsplit lines in vCard, warning about short lines. RFC 2426 page 8.
    @param lines: List of potentially folded vCard lines
    @return: List of lines, one per property
    """
    property_lines = []
    for index in range(len(lines)):
        line = lines[index]
        if len(line) > VCARD_LINE_MAX_LENGTH:
            warnings.warn('Long line at line %i' % index)

        if line.startswith(' '):
            if index == 0:
                raise VCardFormatError(MSG_CONTINUATION_AT_START, 0)
            elif len(lines[index - 1]) < VCARD_LINE_MAX_LENGTH:
                warnings.warn('Short folded line at line %i' % (index - 1))
            property_lines[-1] += line[1:]
        else:
            property_lines.append(line)

    return property_lines

def get_vcard_group(lines):
    """
    Get & validate group. RFC 2426 pages 28, 29.
    @param lines: List of unfolded vCard lines
    @return: Group name if one exists, None otherwise
    """
    group = None

    group_re = re.compile('^([' + ID_CHARS + ']*)\.')

    group_match = group_re.match(lines[0])
    if group_match is not None:
        group = group_match.group(1)

        # Validate
        if len(group) == 0:
            raise VCardFormatError(MSG_DOT_AT_LINE_START)

        for index in range(len(lines)):
            line = lines[index]
            next_match = group_re.match(line)
            if not next_match:
                raise VCardFormatError(MSG_MISSING_GROUP, index)
            if next_match.group(1) != group:
                raise VCardFormatError(
                    MSG_MISMATCH_GROUP + ': %s != %s' % (
                        next_match.group(1),
                        group),
                    index)
    else:
        # Make sure there are no groups elsewhere
        for index in range(len(lines)):
            if group_re.match(lines[index]):
                raise VCardFormatError(
                    MSG_MISMATCH_GROUP + ': %s != %s' % (
                        next_match.group(1),
                        group),
                    index)

    return group

def remove_vcard_groups(lines, group):
    """
    Remove groups from vCard. RFC 2426 pages 28, 29.
    @param lines: List of unfolded vCard lines
    @return: Lines without groups and dot separator
    """
    if group:
        for index in range(len(lines)):
            lines[index] = lines[index][len(group):]
    return lines

def get_vcard_property_param_values(values_string):
    """
    Get the parameter values. RFC 2426 page 29.
    @param text: Comma separated values
    @return: Set of values. Assumes that sequence doesn't matter and that
    duplicate values can be discarded, even though RFC 2426 doesn't explicitly
    say this. I.e., assumes that TYPE=WORK,VOICE,WORK === TYPE=VOICE,WORK.
    """
    values = set(split_unescaped(values_string, ','))

    # Validate
    for value in values:
        if not re.match(
            '^[' + SAFE_CHARS + ']+$|^"[' + QSAFE_CHARS + ']+"$',
            value):
            raise VCardFormatError(MSG_INVALID_VALUE + ': %s' % value)

    return values

def get_vcard_property_param(param_string):
    """
    Get the parameter name and value(s). RFC 2426 page 29.
    @param param_string: Single parameter and values
    @return: Dictionary with a parameter name and values
    """
    parameter_name, values_string = split_unescaped(param_string, '=')
    values = get_vcard_property_param_values(values_string)

    # Validate
    if not re.match('^[' + ID_CHARS + ']+$', parameter_name):
        raise VCardFormatError(MSG_INVALID_PARAM_NAME + ': %s' % parameter_name)

    return {'name': parameter_name, 'values': values}

def get_vcard_property_params(params_string):
    """
    Get the parameters and their values. RFC 2426 page 28.
    @param params_string: Part of a vCard line between the first semicolon
    and the first colon
    @return: Dictionary of parameters. Assumes that
    TYPE=WORK;TYPE=WORK,VOICE === TYPE=VOICE,WORK === TYPE=VOICE;TYPE=WORK.
    """
    params = {}
    if not params_string:
        return params

    for param_string in split_unescaped(params_string, ';'):
        param = get_vcard_property_param(param_string)
        if param['name'] not in params:
            params[param['name']] = param['values']
        else:
            # Merge
            params[param['name']] = params[param['name']] + param['values']

    return params

def get_vcard_property_subvalues(value_string):
    """
    Get the parts of the value
    @param value_string: Single value string
    @return: List of values (RFC 2426 page 9)
    """
    subvalues = split_unescaped(value_string, ',')

    # Validate
    for subvalue in subvalues:
        if not re.match('^[' + VALUE_CHARS + ']*$', subvalue):
            raise VCardFormatError(MSG_INVALID_SUBVALUE + ': %s' % subvalue)

        # TODO: Min / max for specific properties

    return subvalues

def get_vcard_property_values(values_string):
    """
    Get the property values
    @param values_string: Multiple value string
    @return: List of values (RFC 2426 page 12)
    """
    values = []
    subvalue_strings = split_unescaped(values_string, ';')
    for sub in subvalue_strings:
        values.append(get_vcard_property_subvalues(sub))

    # Validate
    for value in values:
        pass # TODO, need to know how many values different properties can have

    return values

def get_vcard_property(property_line):
    """
    Get a single property
    @param property_line: Single unfolded vCard line
    @return: Dictionary with name, parameters and values
    """
    prop = {}

    # Split property and values
    if not property_line:
        raise VCardFormatError(MSG_EMPTY_LINE)
    property_parts = split_unescaped(property_line, ':')
    if len(property_parts) < 2:
        raise VCardFormatError(
            MSG_VALUE_STRING_MISSING + ': %s' % property_line)
    elif len(property_parts) > 2:
        # Merge - Colon doesn't have to be escaped in values
        property_parts[1] = ':'.join(property_parts[1:])
        property_parts = property_parts[:2]
    property_string, values_string = property_parts

    # Split property name and property parameters
    property_name_and_params = split_unescaped(property_string, ';')

    prop['name'] = property_name_and_params.pop(0)

    # Validate
    if not prop['name'] in ALL_PROPERTIES and not re.match(
        '^X-[' + ID_CHARS + ']+$',
        prop['name']):
        raise VCardFormatError(
            MSG_INVALID_PROPERTY_NAME + ': %s' % prop['name'])

    try:
        if len(property_name_and_params) != 0:
            prop['parameters'] = get_vcard_property_params(
                property_name_and_params.pop(0))
        prop['values'] = get_vcard_property_values(values_string)
    except VCardFormatError as error:
        # Add parameter name to error
        raise VCardFormatError(error.message, property_name = prop['name'])

    return prop

def get_vcard_properties(lines):
    """
    Get the properties for each line. RFC 2426 pages 28, 29.
    @param properties: List of unfolded vCard lines
    @return: List of properties, for simplicity. AFAIK sequence doesn't matter
    and duplicates add no information, but ignoring this to make sure
    printed vCards look like the original.
    """
    properties = []
    for property_line in lines:
        properties.append(get_vcard_property(property_line))

    for mandatory_property in ('VERSION', 'N', 'FN'):
        if mandatory_property not in [
            prop['name'] for prop in properties]:
            raise VCardFormatError(
                MSG_MISSING_PROPERTY + ': %s' % mandatory_property,
                property_name = mandatory_property)

    return properties

class VCard():
    """Container for structured and unstructured vCard contents"""
    def __init__(self, text):
        """
        Create vCard object from text string. Includes text (the entire
        unprocessed vCard), group (optional prefix on each line) and properties
        @param text: String containing a single vCard
        """
        if text == '':
            raise VCardFormatError(MSG_EMPTY_VCARD, 0)
        self.text = text

        full_lines = self.text.splitlines(True)
        for index in range(len(full_lines)):
            full_line = full_lines[index]
            if not full_line.endswith(CRLF_CHARS):
                raise VCardFormatError(MSG_INVALID_LINE_SEPARATOR, index)

        lines = unfold_vcard_lines(self.text.splitlines())

        # Groups
        self.group = get_vcard_group(lines)

        # Cleanup
        lines = remove_vcard_groups(lines, self.group)

        # Properties
        try:
            self.properties = get_vcard_properties(lines)
        except VCardFormatError:
            raise

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""vCards v3.0 (RFC 2426) class and parsing + validating functions

Default syntax:

vcard [options] -|file...

Options:
-v,--verbose    Verbose mode

Example:

vcard *.vcf
    Validate all .vcf files in the current directory
"""

import codecs
import getopt
import re
import sys
import warnings

# Local modules
from vcard_defs import \
    ALL_PROPERTIES, \
    CRLF_CHARS, \
    ID_CHARS, \
    MANDATORY_PROPERTIES, \
    MSG_CONTINUATION_AT_START, \
    MSG_DOT_AT_LINE_START, \
    MSG_EMPTY_VCARD, \
    MSG_INVALID_LINE_SEPARATOR, \
    MSG_INVALID_PARAM_NAME, \
    MSG_INVALID_PROPERTY_NAME, \
    MSG_INVALID_SUBVALUE, \
    MSG_INVALID_VALUE, \
    MSG_MISMATCH_GROUP, \
    MSG_MISSING_GROUP, \
    MSG_MISSING_PARAM_VALUE, \
    MSG_MISSING_PROPERTY, \
    MSG_MISSING_VALUE_STRING, \
    QSAFE_CHARS, \
    SAFE_CHARS, \
    SP_CHAR, \
    VALUE_CHARS, \
    VCARD_LINE_MAX_LENGTH_RAW
import vcard_utils
import vcard_validators


def unfold_vcard_lines(lines):
    """
    Unsplit lines in vCard, warning about short lines. RFC 2426 page 8.

    @param lines: List of potentially folded vCard lines
    @return: List of lines, one per property
    """
    property_lines = []
    for index in range(len(lines)):
        line = lines[index]
        if not line.endswith(CRLF_CHARS):
            raise vcard_validators.VCardFormatError(
                MSG_INVALID_LINE_SEPARATOR,
                {'File line': index + 1})
        
        if len(line) > VCARD_LINE_MAX_LENGTH_RAW:
            warnings.warn('Long line in vCard: %s' % line.encode('utf-8'))

        if line.startswith(' '):
            if index == 0:
                raise vcard_validators.VCardFormatError(
                    MSG_CONTINUATION_AT_START,
                    {'File line': index + 1})
            elif len(lines[index - 1]) < VCARD_LINE_MAX_LENGTH_RAW:
                warnings.warn('Short folded line at line %i' % (index - 1))
            elif line == SP_CHAR + CRLF_CHARS:
                warnings.warn('Empty folded line at line %i' % index)
            property_lines[-1] = property_lines[-1][:-len(CRLF_CHARS)] + \
                line[1:]
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
            raise vcard_validators.VCardFormatError(MSG_DOT_AT_LINE_START, {})

        for index in range(len(lines)):
            line = lines[index]
            next_match = group_re.match(line)
            if not next_match:
                raise vcard_validators.VCardFormatError(
                    MSG_MISSING_GROUP,
                    {'File line': index + 1})
            if next_match.group(1) != group:
                raise vcard_validators.VCardFormatError(
                    MSG_MISMATCH_GROUP + ': %s != %s' % (
                        next_match.group(1),
                        group),
                    {'File line': index + 1})
    else:
        # Make sure there are no groups elsewhere
        for index in range(len(lines)):
            if group_re.match(lines[index]):
                raise vcard_validators.VCardFormatError(
                    MSG_MISMATCH_GROUP + ': %s != %s' % (
                        next_match.group(1),
                        group),
                    {'File line': index + 1})

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
    values = set(vcard_utils.split_unescaped(values_string, ','))

    # Validate
    for value in values:
        if not re.match(
            '^[' + SAFE_CHARS + ']+$|^"[' + QSAFE_CHARS + ']+"$',
            value):
            raise vcard_validators.VCardFormatError(
                MSG_INVALID_VALUE + ': %s' % value,
                {})

    return values


def get_vcard_property_param(param_string):
    """
    Get the parameter name and value(s). RFC 2426 page 29.

    @param param_string: Single parameter and values
    @return: Dictionary with a parameter name and values
    """
    try:
        param_name, values_string = vcard_utils.split_unescaped(
            param_string,
            '=')
    except ValueError as error:
        raise vcard_validators.VCardFormatError(
            MSG_MISSING_PARAM_VALUE + ': %s' % error,
            {})

    values = get_vcard_property_param_values(values_string)

    # Validate
    if not re.match('^[' + ID_CHARS + ']+$', param_name):
        raise vcard_validators.VCardFormatError(
            MSG_INVALID_PARAM_NAME + ': %s' % param_name,
            {})

    return {'name': param_name, 'values': values}


def get_vcard_property_params(params_string):
    """
    Get the parameters and their values. RFC 2426 page 28.

    @param params_string: Part of a vCard line between the first semicolon
    and the first colon.
    @return: Dictionary of parameters. Assumes that
    TYPE=WORK;TYPE=WORK,VOICE === TYPE=VOICE,WORK === TYPE=VOICE;TYPE=WORK.
    """
    params = {}
    if not params_string:
        return params

    for param_string in vcard_utils.split_unescaped(params_string, ';'):
        param = get_vcard_property_param(param_string)
        param_name = param['name'].upper() # To be able to merge TYPE & type
        if param_name not in params:
            params[param_name] = param['values']
        else:
            # Merge
            params[param_name] = params[param_name].union(
                param['values'])

    return params


def get_vcard_property_subvalues(value_string):
    """
    Get the parts of the value.

    @param value_string: Single value string
    @return: List of values (RFC 2426 page 9)
    """
    subvalues = vcard_utils.split_unescaped(value_string, ',')

    # Validate string
    for subvalue in subvalues:
        if not re.match('^[' + VALUE_CHARS + ']*$', subvalue):
            raise vcard_validators.VCardFormatError(
                MSG_INVALID_SUBVALUE + ': %s' % subvalue,
                {})

    return subvalues


def get_vcard_property_values(values_string):
    """
    Get the property values.

    @param values_string: Multiple value string
    @return: List of values (RFC 2426 page 12)
    """
    values = []

    # Strip line ending
    values_string = values_string[:-len(CRLF_CHARS)]

    subvalue_strings = vcard_utils.split_unescaped(values_string, ';')
    for sub in subvalue_strings:
        values.append(get_vcard_property_subvalues(sub))

    return values


def get_vcard_property(property_line):
    """
    Get a single property.

    @param property_line: Single unfolded vCard line
    @return: Dictionary with name, parameters and values
    """
    prop = {}

    property_parts = vcard_utils.split_unescaped(property_line, ':')
    if len(property_parts) < 2:
        raise vcard_validators.VCardFormatError(
            MSG_MISSING_VALUE_STRING + ': %s' % property_line,
            {})
    elif len(property_parts) > 2:
        # Merge - Colon doesn't have to be escaped in values
        property_parts[1] = ':'.join(property_parts[1:])
        property_parts = property_parts[:2]
    property_string, values_string = property_parts

    # Split property name and property parameters
    property_name_and_params = vcard_utils.split_unescaped(property_string, ';')

    prop['name'] = property_name_and_params.pop(0)

    # String validation
    if not prop['name'].upper() in ALL_PROPERTIES and not re.match(
        '^X-[' + ID_CHARS + ']+$',
        prop['name'],
        re.IGNORECASE):
        raise vcard_validators.VCardFormatError(
            MSG_INVALID_PROPERTY_NAME + ': %s' % prop['name'],
            {})

    try:
        if len(property_name_and_params) != 0:
            prop['parameters'] = get_vcard_property_params(
                ';'.join(property_name_and_params))
        prop['values'] = get_vcard_property_values(values_string)

        # Validate
        vcard_validators.validate_vcard_property(prop)
    except vcard_validators.VCardFormatError as error:
        # Add parameter name to error
        error.context['Property line'] = property_line
        raise vcard_validators.VCardFormatError(error.message, error.context)

    return prop


def get_vcard_properties(lines):
    """
    Get the properties for each line. RFC 2426 pages 28, 29.

    @param properties: List of unfolded vCard lines
    @return: List of properties, for simplicity. AFAIK sequence doesn't matter
    and duplicates add no information, but ignoring this to make sure vCard
    output looks like the original.
    """
    properties = []
    for index in range(len(lines)):
        property_line = lines[index]
        if property_line != CRLF_CHARS:
            try:
                properties.append(get_vcard_property(property_line))
            except vcard_validators.VCardFormatError as error:
                error.context['vCard line'] = index
                raise vcard_validators.VCardFormatError(
                    error.message,
                    error.context)

    for mandatory_property in MANDATORY_PROPERTIES:
        if mandatory_property not in [
            prop['name'].upper() for prop in properties]:
            raise vcard_validators.VCardFormatError(
                MSG_MISSING_PROPERTY + ': %s' % mandatory_property,
                {'Property': mandatory_property})

    return properties


class VCard():
    """Container for structured and unstructured vCard contents."""
    # pylint: disable-msg=R0903
    def __init__(self, text, filename = None):
        """
        Create vCard object from text string. Includes text (the entire
        unprocessed vCard), group (optional prefix on each line) and properties.

        @param text: String containing a single vCard
        """
        if text == '':
            raise vcard_validators.VCardFormatError(
                MSG_EMPTY_VCARD,
                {'vCard line': 1, 'File line': 1})

        self.text = text

        self.filename = filename

        lines = unfold_vcard_lines(self.text.splitlines(True))

        # Groups
        self.group = get_vcard_group(lines)
        lines = remove_vcard_groups(lines, self.group)

        # Properties
        self.properties = get_vcard_properties(lines)

    def __str__(self):
        return self.text


def validate_file(filename, verbose = False):
    """
    Create object for each vCard in a file, and show the error output.

    @param filename: Path to file
    @param verbose: Verbose mode
    @return: Debugging output from creating vCards
    """
    if filename == '-':
        file_pointer = sys.stdin
    else:
        file_pointer = codecs.open(filename, 'r', 'utf-8')

    contents = file_pointer.read().splitlines(True)

    vcard_text = ''
    result = ''
    try:
        for index in range(len(contents)):
            line = contents[index]
            vcard_text += line

            if line == CRLF_CHARS:
                try:
                    vcard = VCard(vcard_text, filename)
                    vcard_text = ''
                    if verbose:
                        print(vcard)
                except vcard_validators.VCardFormatError as error:
                    error.context['File'] = filename
                    error.context['File line'] = index
                    raise vcard_validators.VCardFormatError(
                        error.message,
                        error.context)

    except vcard_validators.VCardFormatError as error:
        result += unicode(error.__str__())

    if vcard_text != '' and result == '':
        result += 'Could not process entire %s - %i lines remain' % (
            filename,
            len(vcard_text.splitlines()))

    if result == '':
        return None
    return result


class Usage(Exception):
    """Raise in case of invalid parameters."""
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


def main(argv = None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    verbose = False

    try:
        try:
            opts, args = getopt.getopt(
                argv[1:],
                'v',
                ['verbose'])
        except getopt.GetoptError, err:
            raise Usage(err.message)

        if len(opts) != 0:
            for option in opts[0]:
                if option in ('-v', '--verbose'):
                    verbose = True
                else:
                    raise Usage('Unhandled option %s' % option)

        if not args:
            raise Usage(__doc__)

    except Usage, err:
        sys.stderr.write(err.message + '\n')
        return 2

    for filename in args:
        result = validate_file(filename, verbose)
        if result is not None:
            print(result.encode('utf-8') + '\n')


if __name__ == '__main__':
    sys.exit(main())

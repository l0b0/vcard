# -*- coding: utf-8 -*-

import sys

# Error literals

# General
NOTE_EMPTY_VCARD = 'vCard is empty'

# Lines
NOTE_CONTINUATION_AT_START = 'Continuation line at start of vCard (See RFC 2425 section 5.8.1 for line folding details)'
NOTE_INVALID_LINE_SEPARATOR = 'Invalid line ending; should be \\r\\n (See RFC 2426 section 2.4.2 for details)'
NOTE_DOT_AT_LINE_START = 'Dot at start of line without group name (See RFC 2426 section 4 for group syntax)'
NOTE_MISSING_GROUP = 'Missing group (See RFC 2426 section 4 for contentline syntax)'

# Item counts & Length
NOTE_NON_EMPTY_PARAMETER = 'Property should not have parameters (See RFC 2426 section 3 for details)'
NOTE_INVALID_SUB_VALUE_COUNT = 'Invalid sub-value count (See RFC 2426 section 3 for details)'
NOTE_INVALID_VALUE_COUNT = 'Invalid value count (See RFC 2426 section 3 for details)'
NOTE_MISSING_PARAMETER = 'Parameter missing (See RFC 2426 section 3 for details)'
NOTE_MISSING_PARAM_VALUE = 'Parameter value missing (See RFC 2426 section 3 for details)'
NOTE_MISSING_PROPERTY = 'Mandatory property missing (See RFC 2426 section 5 for details)'
NOTE_MISSING_VALUE_STRING = 'Missing value string (See RFC 2426 section 4 for contentline syntax)'

# Names
NOTE_INVALID_PROPERTY_NAME = 'Invalid property name (See RFC 2426 section 4 for name syntax)'
NOTE_INVALID_X_NAME = 'Invalid X-name (See RFC 2426 section 4 for x-name syntax)'
NOTE_INVALID_PARAMETER_NAME = 'Invalid parameter name (See RFC 2426 section 4 for param-name syntax)'
NOTE_MISMATCH_GROUP = 'Group mismatch (See RFC 2426 section 4 for contentline syntax)'

# Values & Sub-values
NOTE_INVALID_PARAMETER_VALUE = 'Invalid parameter value (See RFC 2426 section 4 for param-value syntax)'
NOTE_MISMATCH_PARAMETER = 'Parameter mismatch (See RFC 2426 section 3 for details)'
NOTE_INVALID_DATE = 'Invalid date (See RFC 2425 section 5.8.4 for date syntax)'
NOTE_INVALID_LANGUAGE_VALUE = 'Invalid language (See RFC 1766 section 2 for details)'
NOTE_INVALID_SUB_VALUE = 'Invalid sub-value (See RFC 2426 section 3 for details)'
NOTE_INVALID_TEXT_VALUE = 'Invalid text value (See RFC 2426 section 4 for details)'
NOTE_INVALID_TIME = 'Invalid time (See RFC 2425 section 5.8.4 for time syntax)'
NOTE_INVALID_TIME_ZONE = 'Invalid time zone (See RFC 2426 section 3.4.1 for time-zone syntax)'
NOTE_INVALID_URI = 'Invalid URI (See RFC 1738 section 5 for genericurl syntax)'
NOTE_INVALID_VALUE = 'Invalid value (See RFC 2426 section 3 for details)'

# Warning literals
WARN_DEFAULT_TYPE_VALUE = 'Using default TYPE value; can be removed'
WARN_INVALID_DATE = 'Possible invalid date'
WARN_INVALID_EMAIL_TYPE = 'Possible invalid email TYPE'
WARN_MULTIPLE_NAMES = 'Possible split name (replace space with comma)'


def _stringify(text):
    """
    Get the text as a string representation

    @param text: Something convertible to str
    @return: Printable string
    """
    try:
        text = str(text)
    except UnicodeEncodeError:
        text = text.encode('utf-8')
    return text


def show_warning(
    message,
    category=UserWarning,
    filename='',
    lineno=-1,
    file=sys.stderr,
    line=None
):
    """Custom simple warning."""
    file.write('{0}\n'.format(message))


class VCardError(Exception):
    """Raised if the text given is not a valid according to RFC 2426."""
    def __init__(self, message, context):
        """
        vCard format error.

        @param message: Error message
        @param context: Dictionary with context information
        """
        Exception.__init__(self)
        self.message = message
        self.context = context

    def __str__(self):
        """
        Outputs error with ordered context info.

        @return: Printable error message
        """
        message = _stringify(self.message)

        # Sort context information
        keys = ['File', 'File line', 'vCard line', 'Property', 'Property line', 'String']
        for key in keys:
            if key in self.context:
                message += '\n{0}: {1}'.format(_stringify(key), _stringify(self.context.pop(key)))

        return message


class VCardLineError(VCardError):
    """Raised for line-related errors."""
    pass


class VCardNameError(VCardError):
    """Raised for name-related errors."""
    pass


class VCardValueError(VCardError):
    """Raised for value-related errors."""
    pass


class VCardItemCountError(VCardError):
    """Raised when a required number of something is not present."""
    pass


class UsageError(Exception):
    """Raise in case of invalid parameters."""
    def __init__(self, message):
        Exception.__init__(self)
        self._message = message

    def __str__(self):
        return self._message

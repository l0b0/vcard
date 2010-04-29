#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General purpose utility functions"""

import re


def find_unescaped(text, char, escape_char = '\\'):
    """
    Find occurrence of an unescaped character.

    @param text: String
    @param char: Character to find
    @param escape_char: Escape character
    @return: Index of first match, None if no match
    
    Examples:
    >>> find_unescaped('BEGIN:VCARD', ':')
    5
    >>> find_unescaped('foo\\\\,bar,baz', ',')
    8
    >>> find_unescaped(r'foo\\,bar,baz', ',')
    8
    >>> find_unescaped('foo\\\\\\\\,bar,baz', ',')
    5
    >>> find_unescaped('foo,bar,baz', ':')
    >>> find_unescaped('foo\\\\,bar\\\\,baz', ',')
    """
    unescaped_regex = '(?<!' + escape_char + escape_char + ')' + \
            '(?:' + escape_char + escape_char + escape_char + escape_char + \
            ')*' + \
            '(' + char + ')'
    regex = re.compile(unescaped_regex)

    char_match = regex.search(text)

    if char_match is None:
        return None
    return char_match.start(1)


def split_unescaped(text, separator, escape_char = '\\\\'):
    """
    Find strings separated by an unescaped character.

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
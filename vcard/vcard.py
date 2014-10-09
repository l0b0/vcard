#!/usr/bin/env python
import argparse

import sys

from vcard_validator import VcardValidator
from vcard_errors import UsageError

PATH_ARGUMENT_HELP = "The files to validate. Use '-' for standard input"
VERBOSE_OPTION_HELP = 'Enable verbose output'


def main():
    try:
        arguments = parse_arguments(sys.argv[1:])
    except UsageError as error:
        sys.stderr.write('{0}\n'.format(str(error)))
        return 2

    for filename in arguments.paths:
        print VcardValidator(filename, arguments.verbose).result


def parse_arguments(arguments):
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--verbose', default=False, action='store_true', help=VERBOSE_OPTION_HELP)
    argument_parser.add_argument('paths', metavar='path', nargs='+', help=PATH_ARGUMENT_HELP)
    try:
        parsed_arguments = argument_parser.parse_args(args=arguments)
    except argparse.ArgumentError as error:
        raise UsageError(str(error))
    return parsed_arguments


if __name__ == '__main__':
    sys.exit(main())

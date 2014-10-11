import argparse
from unittest import TestCase
import mock

from vcard import vcard

ARGUMENTS_WITH_PATH = argparse.Namespace(paths=['any'], verbose=False)
ARGUMENTS_WITH_PATHS = argparse.Namespace(paths=['any', 'another'], verbose=False)


class TestVcard(TestCase):
    @mock.patch('vcard.vcard.parse_arguments')
    @mock.patch('vcard.vcard.VcardValidator', spec=vcard.VcardValidator)
    def test_main_succeeds_when_vcard_validator_returns_nothing(self, vcard_validator_mock, parse_arguments_mock):
        parse_arguments_mock.return_value = ARGUMENTS_WITH_PATH
        vcard_validator_mock.return_value.result = None
        self.assertEqual(0, vcard.main())

    @mock.patch('vcard.vcard.parse_arguments')
    @mock.patch('vcard.vcard.VcardValidator', spec=vcard.VcardValidator)
    def test_main_fails_when_vcard_validator_fails(self, vcard_validator_mock, parse_arguments_mock):
        parse_arguments_mock.return_value = ARGUMENTS_WITH_PATH
        vcard_validator_mock.return_value.result = 'non-empty'
        self.assertEqual(1, vcard.main())

    @mock.patch('vcard.vcard.parse_arguments')
    @mock.patch('vcard.vcard.VcardValidator')
    def test_main_fails_when_vcard_validator_fails_on_first_file(self, vcard_validator_mock, parse_arguments_mock):
        parse_arguments_mock.return_value = ARGUMENTS_WITH_PATHS
        vcard_validator_mock.side_effect = [
            mock.Mock(spec=vcard.VcardValidator, result='non-empty'),
            mock.Mock(spec=vcard.VcardValidator, result=None)]
        self.assertEqual(1, vcard.main())

    @mock.patch('vcard.vcard.parse_arguments')
    def test_main_fails_when_argument_parsing_fails(self, parse_arguments_mock):
        parse_arguments_mock.side_effect = vcard.UsageError('error')
        self.assertEqual(2, vcard.main())

    def test_parse_arguments_succeeds_with_single_path(self):
        path = '/some/path'
        expected_paths = [path]

        actual_paths = vcard.parse_arguments([path]).paths

        self.assertEqual(expected_paths, actual_paths)

    def test_parse_arguments_succeeds_with_multiple_paths(self):
        path1 = '/some/path'
        path2 = '/other/path'
        arguments = [path1, path2]
        expected_paths = arguments

        actual_paths = vcard.parse_arguments(arguments).paths

        self.assertEqual(expected_paths, actual_paths)

    def test_parse_arguments_fails_without_path(self):
        self.assertRaises(SystemExit, vcard.parse_arguments, [])

    def test_parse_arguments_fails_with_invalid_argument(self):
        self.assertRaises(SystemExit, vcard.parse_arguments, ['--foo'])

    def test_parse_arguments_verbose_off_by_default(self):
        path = '/some/path'

        actual_verbosity = vcard.parse_arguments([path]).verbose

        self.assertFalse(actual_verbosity)

    def test_parse_arguments_sets_verbose_when_passed(self):
        path = '/some/path'

        actual_verbosity = vcard.parse_arguments(['--verbose', path]).verbose

        self.assertTrue(actual_verbosity)

from unittest import TestCase

from vcard import vcard


class TestVcard(TestCase):
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

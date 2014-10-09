import mock
from unittest import TestCase
from vcard import vcard_validator


class TestVcardValidator(TestCase):
    @mock.patch('vcard.vcard_validator.validate_file')
    def test_result_from_validator(self, validate_file_mock):
        validate_file_mock.return_value = 'foo'

        validator = vcard_validator.VcardValidator('/some/path', False)

        self.assertEqual(validator.result, 'foo')

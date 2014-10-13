from unittest import TestCase
from vcard.vcard_errors import VCardValueError
from vcard.vcard_validators import validate_date


class TestVcardValidators(TestCase):
    def test_validate_date_succeeds_with_valid_date_without_separators(self):
        date_string = '19990101'
        validate_date(date_string)

    def test_validate_date_succeeds_with_valid_date_with_separators(self):
        date_string = '1999-01-01'
        validate_date(date_string)

    def test_validate_date_succeeds_with_leap_day(self):
        date_string = '2008-02-29'
        validate_date(date_string)

    def test_validate_date_succeeds_with_leap_day_in_year_divisible_by_four_hundred(self):
        date_string = '2000-02-29'
        validate_date(date_string)

    def test_validate_date_fails_with_leap_day_in_year_not_divisible_by_four(self):
        date_string = '2010-02-29'
        self.assertRaises(VCardValueError, validate_date, date_string)

    def test_validate_date_fails_with_leap_day_in_year_divisible_by_one_hundred(self):
        date_string = '1900-02-29'
        self.assertRaises(VCardValueError, validate_date, date_string)

    def test_validate_date_fails_with_wrong_separator(self):
        date_string = '1999:01:01'
        self.assertRaises(VCardValueError, validate_date, date_string)

    def test_validate_date_fails_with_shortened_date(self):
        date_string = '1999101'
        self.assertRaises(VCardValueError, validate_date, date_string)

    def test_validate_date_fails_with_nonsense_date(self):
        date_string = 'aaaa-bb-cc'
        self.assertRaises(VCardValueError, validate_date, date_string)

    def test_validate_date_error_explains_itself(self):
        date_string = '1999:01:01'
        try:
            validate_date(date_string)
        except VCardValueError as error:
            self.assertIn('Invalid date', str(error))

    def test_validate_date_error_contains_date(self):
        date_string = '1999:01:01'
        try:
            validate_date(date_string)
        except VCardValueError as error:
            self.assertIn(date_string, str(error))

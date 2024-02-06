import unittest
from todo.src.app import validate_date


class TestValidateDate(unittest.TestCase):
    def test_valid_date(self):
        self.assertTrue(validate_date("2022-12-31"))
        self.assertTrue(validate_date("2024-02-29"))

    def test_invalid_date(self):
        self.assertFalse(validate_date("2022-12-32"))
        self.assertFalse(validate_date("2022-13-31"))
        self.assertFalse(validate_date("31-12-2022"))
        self.assertFalse(validate_date("02-2022-30"))

    def test_invalid_format(self):
        self.assertFalse(validate_date("2022/12/31"))
        self.assertFalse(validate_date("2022-12-31T00:00:00"))


if __name__ == "__main__":
    unittest.main()

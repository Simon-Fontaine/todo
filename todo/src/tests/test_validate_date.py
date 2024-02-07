import unittest
from todo.src.app import validate_date


class TestValidateDate(unittest.TestCase):
    def test_valid_date(self):
        result = validate_date("2022-12-31")
        self.assertTrue(result)

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            validate_date("2022-12-32")

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            validate_date("2022/12/31")


if __name__ == "__main__":
    unittest.main()

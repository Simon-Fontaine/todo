import random
import string
import unittest

from todo.src.app import mark_as_done, add_todo, drop_user_collection


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestMarkAsDoneTodo(unittest.TestCase):
    def setUp(self):
        self.user = get_random_string(20)
        self.todo = get_random_string(20)
        self.priority = "low"
        self.end_date = "2022-12-31"
        self.todo_id = add_todo(self.user, self.todo, self.priority, self.end_date)

    def tearDown(self):
        drop_user_collection(self.user)

    def test_mark_as_done(self):
        result = mark_as_done(self.user, self.todo_id)
        self.assertTrue(result)

    def test_mark_as_done_invalid_id(self):
        with self.assertRaises(Exception):
            mark_as_done(self.user, "invalid_id")


if __name__ == "__main__":
    unittest.main()

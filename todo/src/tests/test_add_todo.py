import random
import string
import unittest

from todo.src.app import add_todo, drop_user_collection


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestAddTodo(unittest.TestCase):
    def setUp(self):
        self.user = get_random_string(20)
        self.todo = get_random_string(20)
        self.priority = "low"
        self.end_date = "2022-12-31"

    def tearDown(self):
        drop_user_collection(self.user)

    def test_add_todo(self):
        todo_id = add_todo(self.user, self.todo, self.priority, self.end_date)
        self.assertIsNotNone(todo_id)

    def test_add_todo_no_end_date(self):
        todo_id = add_todo(self.user, self.todo, self.priority, None)
        self.assertIsNotNone(todo_id)

    def test_add_todo_invalid_end_date(self):
        with self.assertRaises(ValueError):
            add_todo(self.user, self.todo, self.priority, "2022-12-32")


if __name__ == "__main__":
    unittest.main()

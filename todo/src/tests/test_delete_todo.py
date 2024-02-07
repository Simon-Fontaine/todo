import random
import string
import unittest

from todo.src.app import delete_todo, add_todo, drop_user_collection


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestDeleteTodo(unittest.TestCase):
    def setUp(self):
        self.user = get_random_string(20)
        self.todo = get_random_string(20)
        self.priority = "low"
        self.end_date = "2022-12-31"
        self.todo_id = add_todo(self.user, self.todo, self.priority, self.end_date)

    def tearDown(self):
        drop_user_collection(self.user)

    def test_delete_todo(self):
        result = delete_todo(self.user, self.todo_id)
        self.assertTrue(result)

    def test_delete_todo_with_invalid_id(self):
        with self.assertRaises(Exception):
            delete_todo(self.user, "invalid_id")


if __name__ == "__main__":
    unittest.main()

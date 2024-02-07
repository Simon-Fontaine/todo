import random
import string
import unittest

from todo.src.app import list_todos, add_todo, drop_user_collection


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestListTodos(unittest.TestCase):
    def setUp(self):
        self.user = get_random_string(20)
        self.descriptions = ["test0", "test1", "test2", "test3"]
        self.priorities = ["low", "medium", "high", "low"]
        self.dates = ["2022-12-31", "2023-10-05", "2024-02-07", "2022-01-01"]

        for description, priority, date in zip(
            self.descriptions, self.priorities, self.dates
        ):
            add_todo(self.user, description, priority, date)

    def tearDown(self):
        drop_user_collection(self.user)

    def test_list_todos(self):
        result = list_todos(self.user)
        todos = list(result)
        self.assertEqual(len(todos), len(self.descriptions))

    def test_list_todos_empty(self):
        drop_user_collection(self.user)
        result = list_todos(self.user)
        todos = list(result)
        self.assertEqual(len(todos), 0)

    def test_list_sorted_date(self):
        result = list_todos(self.user, sort=True)
        todos = list(result)
        self.assertEqual(len(todos), len(self.descriptions))

        for i in range(len(todos) - 1):
            self.assertLessEqual(todos[i]["end_date"], todos[i + 1]["end_date"])

    def test_list_filter_priority(self):
        priority_to_test = "low"
        result = list_todos(self.user, priority=priority_to_test)
        todos = list(result)
        self.assertEqual(len(todos), self.priorities.count(priority_to_test))

        for todo in result:
            self.assertEqual(todo["priority"], priority_to_test)


if __name__ == "__main__":
    unittest.main()

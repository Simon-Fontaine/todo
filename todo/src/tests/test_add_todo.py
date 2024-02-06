import os
import random
import string
import pymongo
import unittest

from todo.src.app import add_todo
from dotenv import load_dotenv

load_dotenv()


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestAddTodo(unittest.TestCase):
    def setUp(self):
        self.mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        self.mongo_database = self.mongo_client["todo"]
        self.user = get_random_string(20)
        self.todo = get_random_string(20)
        self.priority = "low"
        self.end_date = "2022-12-31"

    def tearDown(self):
        self.mongo_database[self.user].drop()

    def test_add_todo(self):
        add_todo(self.user, self.todo, self.priority, self.end_date)
        self.assertTrue(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                }
            )
        )

    def test_add_todo_with_no_end_date(self):
        end_date = None

        add_todo(
            self.user,
            self.todo,
            self.priority,
            end_date,
        )
        self.assertTrue(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": end_date,
                }
            )
        )

    def test_add_todo_wrong_date_format(self):
        end_date = "2022/12/31"

        add_todo(
            self.user,
            self.todo,
            self.priority,
            end_date,
        )
        self.assertFalse(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": end_date,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()

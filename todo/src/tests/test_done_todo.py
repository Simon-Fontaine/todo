import os
import random
import string
import pymongo
import unittest

from bson.objectid import ObjectId
from todo.src.app import mark_todo_as_done
from dotenv import load_dotenv

load_dotenv()


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestMarkAsDoneTodo(unittest.TestCase):
    def setUp(self):
        self.mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        self.mongo_database = self.mongo_client["todo"]
        self.user = get_random_string(20)
        self.todo = get_random_string(20)
        self.priority = "low"
        self.end_date = "2022-12-31"

        testData = self.mongo_database[self.user].insert_one(
            {
                "todo": self.todo,
                "priority": self.priority,
                "end_date": self.end_date,
            }
        )
        self.todo_id = ObjectId(testData.inserted_id)

    def tearDown(self):
        self.mongo_database[self.user].drop()

    def test_mark_as_done(self):
        self.assertFalse(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                    "done": True,
                }
            )
        )

        mark_todo_as_done(self.user, self.todo_id)
        self.assertTrue(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                    "done": True,
                }
            )
        )

    def test_mark_as_done_invalid_id(self):
        invalid_id = ObjectId()

        self.assertFalse(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                    "done": True,
                }
            )
        )

        mark_todo_as_done(self.user, invalid_id)
        self.assertFalse(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                    "done": True,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()

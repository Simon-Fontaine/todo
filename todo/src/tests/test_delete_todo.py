import os
import random
import string
import pymongo
import unittest

from bson.objectid import ObjectId
from todo.src.app import delete_todo
from dotenv import load_dotenv

load_dotenv()


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class TestDeleteTodo(unittest.TestCase):
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

    def test_delete_todo(self):
        self.assertTrue(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                }
            )
        )

        delete_todo(self.user, self.todo_id)
        self.assertFalse(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                }
            )
        )

    def test_delete_todo_with_invalid_id(self):
        invalid_id = ObjectId()

        self.assertFalse(self.mongo_database[self.user].find_one(({"_id": invalid_id})))
        self.assertFalse(delete_todo(self.user, invalid_id))
        self.assertTrue(
            self.mongo_database[self.user].find_one(
                {
                    "todo": self.todo,
                    "priority": self.priority,
                    "end_date": self.end_date,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()

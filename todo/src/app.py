import os
import enum
import pymongo
from dotenv import load_dotenv


class Action(enum.Enum):
    LIST = 0
    ADD = 1


load_dotenv()

mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
mongo_database = mongo_client["todo"]


def get_todos(user: str):
    return mongo_database[user].find()


def add_todo(user: str, todo: str):
    mongo_database[user].insert_one({"todo": todo})


def list_todos(user: str):
    todos = get_todos(user)
    for todo in todos:
        print(todo["todo"])


def add_todo_input(user: str):
    todo = input("What do you want to add? ")
    add_todo(user, todo)


def invalid_action():
    print("Invalid action")


actions = {
    Action.LIST: list_todos,
    Action.ADD: add_todo_input,
}


def app(user: str, action: Action):
    actions.get(action, invalid_action)(user)

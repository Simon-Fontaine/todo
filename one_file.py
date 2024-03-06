import json
import pymongo
import argparse
from rich import box
from rich.table import Table
from datetime import datetime
from rich.console import Console
from rich.padding import Padding
from bson.objectid import ObjectId, InvalidId
from importlib.metadata import version

CONSOLE = Console()
with open("secrets.json") as file:
    SECRETS = json.load(file)
MONGO_CLIENT = pymongo.MongoClient(SECRETS["mongo_uri"])
MONGO_DATABASE = MONGO_CLIENT["todo"]


def handle_error(error_message, error=None) -> None:
    message = f"[bold red][ERROR][/bold red] {error_message}"
    if error:
        message += f" [black](Details: {error})[black]"
    CONSOLE.print(Padding(message, (1, 0, 1, 0)))


def handle_success(success_message, id=None) -> None:
    message = f"[bold green][SUCCESS][/bold green] {success_message}"
    if id:
        message += f" [black](id: {id})[black]"
    CONSOLE.print(Padding(message, (1, 0, 1, 0)))


def display_todo_list(cursor) -> None:
    TODOS = list(cursor)

    TABLE = Table(
        min_width=75,
        row_styles=["none"],
        border_style="cyan",
        header_style="bold yellow",
        footer_style="bold black",
        box=box.SIMPLE,
        show_footer=True,
    )
    TABLE.add_column("End Date")
    TABLE.add_column("Todo")
    TABLE.add_column("Priority")
    TABLE.add_column("Done")
    TABLE.add_column("ID")

    for todo in TODOS:
        TABLE.add_row(
            format_datetime(todo["end_date"]),
            todo["todo"],
            todo["priority"],
            (
                "[bold green]Yes[/bold green]"
                if todo["done"]
                else "[bold red]No[/bold red]"
            ),
            str(todo["_id"]),
        )

    DONE_TODOS = sum(todo["done"] for todo in TODOS)
    NUM_RESULTS = len(TODOS)
    COMPLETION_PERCENTAGE = round(DONE_TODOS / NUM_RESULTS * 100) if NUM_RESULTS else 0
    TABLE.caption = (
        f"{COMPLETION_PERCENTAGE} % Completed ( {DONE_TODOS} / {NUM_RESULTS} )"
    )

    CONSOLE.print(TABLE)


def drop_user_collection(user: str) -> None:
    MONGO_DATABASE.drop_collection(user.lower())


def valid_object_id(id_str):
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise argparse.ArgumentTypeError("Invalid ObjectId.")


def validate_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d") if dt else None


def add_todo(
    user: str, todo: str, priority: str, end_date: datetime | None
) -> ObjectId:
    RESULT = MONGO_DATABASE[user.lower()].insert_one(
        {
            "todo": todo,
            "priority": priority,
            "end_date": end_date,
            "done": False,
        }
    )

    return RESULT.inserted_id


def delete_todo(user: str, todo_id: ObjectId) -> int:
    try:
        RESULT = MONGO_DATABASE[user.lower()].delete_one({"_id": todo_id})
        return RESULT.deleted_count
    except InvalidId:
        raise ValueError("Invalid todo ID")


def mark_as_done(user: str, todo_id: ObjectId) -> int:
    try:
        RESULT = MONGO_DATABASE[user.lower()].update_one(
            {"_id": todo_id}, {"$set": {"done": True}}
        )
        return RESULT.modified_count
    except InvalidId:
        raise ValueError("Invalid todo ID")


def list_todos(user: str, sort: bool = False, priority: str = None):
    QUERY = {"priority": priority} if priority else {}
    CURSOR = MONGO_DATABASE[user.lower()].find(QUERY)

    if sort:
        CURSOR.sort("end_date", pymongo.ASCENDING)

    return CURSOR


def handle_action(ARGS):
    try:
        if ARGS.action == "add":
            END_DATE = validate_date(ARGS.end_date) if ARGS.end_date else None
            if ARGS.end_date and not END_DATE:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD")

            TODO_ID = add_todo(ARGS.user, ARGS.todo, ARGS.priority, END_DATE)
            return handle_success("Todo added successfully", TODO_ID)
        elif ARGS.action == "delete":
            DELETED_COUNT = delete_todo(ARGS.user, ObjectId(ARGS.todo_id))
            return handle_success(
                f"{DELETED_COUNT} Todo deleted successfully", ARGS.todo_id
            )
        elif ARGS.action == "done":
            MODIFIED_COUNT = mark_as_done(ARGS.user, ObjectId(ARGS.todo_id))
            return handle_success(f"{MODIFIED_COUNT} Todo marked as done", ARGS.todo_id)
        elif ARGS.action == "list":
            CURSOR = list_todos(ARGS.user, ARGS.sort, ARGS.priority)
            return display_todo_list(CURSOR)
        else:
            return handle_error("Invalid action")
    except (ValueError, InvalidId) as e:
        return handle_error(str(e))
    except pymongo.errors.PyMongoError as e:
        return handle_error("Database error", str(e))
    except Exception as e:
        return handle_error("Unexpected error", str(e))


def main():
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument("-v", "--version", action="store_true")

    SUB_PARSERS = PARSER.add_subparsers(dest="action")

    # Add subparsers
    ADD_PARSER = SUB_PARSERS.add_parser("add")
    ADD_PARSER.add_argument("user", metavar="user")
    ADD_PARSER.add_argument("todo", metavar="todo")
    ADD_PARSER.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        default="low",
    )
    ADD_PARSER.add_argument("--end-date")

    # Delete subparsers
    DELETE_PARSER = SUB_PARSERS.add_parser("delete")
    DELETE_PARSER.add_argument("user", metavar="user")
    DELETE_PARSER.add_argument("todo_id", type=valid_object_id)

    # Done subparsers
    DONE_PARSER = SUB_PARSERS.add_parser("done")
    DONE_PARSER.add_argument("user", metavar="user")
    DONE_PARSER.add_argument("todo_id", type=valid_object_id)

    # List subparsers
    LIST_PARSER = SUB_PARSERS.add_parser("list")
    LIST_PARSER.add_argument("user", metavar="user")
    LIST_PARSER.add_argument("--sort", action="store_true")
    LIST_PARSER.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
    )

    ARGS = PARSER.parse_args()

    if ARGS.version:
        TODO_VERSION = version("todo")
        return handle_success(f"Current version: {TODO_VERSION}")
    elif ARGS.action in ["add", "delete", "done", "list"]:
        return handle_action(ARGS)
    else:
        return CONSOLE.print(PARSER.format_help())


if __name__ == "__main__":
    main()

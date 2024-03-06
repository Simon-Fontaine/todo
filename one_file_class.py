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


class TodoApp:
    def __init__(self, user: str = "default", secrets_file="secrets.json"):
        with open(secrets_file) as file:
            secrets = json.load(file)
        self.client = pymongo.MongoClient(secrets["mongo_uri"])
        self.db = self.client["todo"]
        self.collection = self.db[user.lower()]

    def add(self, todo: str, priority: str = "low", end_date_str: str = None):
        end_date = validate_date(end_date_str) if end_date_str else None
        if end_date_str and not end_date:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD")

        result = self.collection.insert_one(
            {"todo": todo, "priority": priority, "end_date": end_date, "done": False}
        )
        return result.inserted_id

    def delete(self, id: ObjectId):
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count

    def done(self, id: ObjectId):
        result = self.collection.update_one({"_id": id}, {"$set": {"done": True}})
        return result.modified_count

    def list(self, sort: bool = False, priority: str = None, done: bool = None):
        query = {}
        if priority:
            query["priority"] = priority
        if done is not None:
            query["done"] = done
        cursor = self.collection.find(query)
        if sort:
            cursor.sort("end_date", pymongo.ASCENDING)

        return list(cursor)


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
        try:
            app = TodoApp(ARGS.user)
            if ARGS.action == "add":
                todo_id = app.add(ARGS.todo, ARGS.priority, ARGS.end_date)
                return handle_success("Todo added", todo_id)
            elif ARGS.action == "delete":
                deleted_count = app.delete(ARGS.todo_id)
                return handle_success(f"Deleted {deleted_count} todo")
            elif ARGS.action == "done":
                modified_count = app.done(ARGS.todo_id)
                return handle_success(f"Marked {modified_count} todo as done")
            elif ARGS.action == "list":
                return display_todo_list(app.list(ARGS.sort, ARGS.priority))
        except (ValueError, InvalidId) as e:
            return handle_error(str(e))
        except pymongo.errors.PyMongoError as e:
            return handle_error("Database error", str(e))
        except Exception as e:
            return handle_error("Unexpected error", str(e))
    else:
        return CONSOLE.print(PARSER.format_help())


if __name__ == "__main__":
    main()

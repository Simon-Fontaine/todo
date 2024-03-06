import json
import pymongo
from rich import box
from rich.padding import Padding
from bson.objectid import ObjectId
from rich.table import Table
from datetime import datetime


with open("secrets.json") as f:
    secrets = json.load(f)
mongo_client = pymongo.MongoClient(secrets["mongo_uri"])
mongo_database = mongo_client["todo"]


def drop_user_collection(user: str):
    mongo_database[user.lower()].drop()


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_datetime(dt: datetime) -> str:
    """Consistently format datetimes for display"""
    return dt.strftime("%Y-%m-%d") if dt else None


def add_todo(user: str, todo: str, priority: str, end_date: str = None) -> str:
    try:
        if end_date is not None and not validate_date(end_date):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD")

        result = mongo_database[user.lower()].insert_one(
            {
                "todo": todo,
                "priority": priority,
                "end_date": (
                    datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
                ),
                "done": False,
            }
        )
        return str(result.inserted_id)
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        raise Exception(f"Failed to add todo: {str(e)}")


def delete_todo(user: str, todo_id: str) -> int:
    try:
        result = mongo_database[user.lower()].delete_one({"_id": ObjectId(todo_id)})
        return result.deleted_count
    except Exception as e:
        raise Exception(f"Failed to delete todo: {str(e)}")


def list_todos(user: str, sort: bool = False, priority: str = None):
    try:
        query = {"priority": priority} if priority else {}
        cursor = mongo_database[user.lower()].find(query)

        if sort:
            cursor = cursor.sort("end_date", pymongo.ASCENDING)

        return cursor
    except Exception as e:
        raise Exception(f"Failed to list todos: {str(e)}")


def mark_as_done(user: str, todo_id: str) -> int:
    try:
        result = mongo_database[user.lower()].update_one(
            {"_id": ObjectId(todo_id)}, {"$set": {"done": True}}
        )
        return result.modified_count
    except Exception as e:
        raise Exception(f"Failed to mark todo as done: {str(e)}")


def display_error(console, message: str = "An error occurred", id: str = None):
    message = (
        f"[bold red][ERROR][/bold red] {message} [black](id: {id})[black]"
        if id
        else f"[bold red][ERROR][/bold red] {message}"
    )

    console.print(Padding(message, (1, 0, 1, 0)))


def display_success(console, message: str = "Operation successful", id: str = None):
    message = (
        f"[bold green][SUCCESS][/bold green] {message} [black](id: {id})[black]"
        if id
        else f"[bold green][SUCCESS][/bold green] {message}"
    )

    console.print(Padding(message, (1, 0, 1, 0)))


def display_table(console, results):
    results = list(results)

    table = Table(
        min_width=75,
        row_styles=["none"],
        border_style="cyan",
        header_style="bold yellow",
        footer_style="bold black",
        box=box.SIMPLE,
        show_footer=True,
    )
    table.add_column("End Date")
    table.add_column("Todo")
    table.add_column("Priority")
    table.add_column("Done")
    table.add_column("ID")

    for todo in results:
        table.add_row(
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

    done_todos = sum(1 for todo in results if todo["done"])
    num_results = len(results)
    completion_percentage = round(done_todos / num_results * 100) if num_results else 0
    table.caption = (
        f"{completion_percentage} % Completed ( {done_todos} / {num_results} )"
    )

    console.print(table)


def app(console, args):
    try:
        if args.action == "add":
            todo_id = add_todo(
                args.user.lower(), args.todo, args.priority, args.end_date
            )
            display_success(console, "Todo added successfully", todo_id)
        elif args.action == "delete":
            deleted_count = delete_todo(args.user.lower(), args.todo_id)
            if deleted_count:
                display_success(console, "Todo deleted successfully", args.todo_id)
            else:
                display_error(console, "Todo not found", args.todo_id)
        elif args.action == "list":
            results = list_todos(args.user.lower(), args.sort, args.priority)
            display_table(console, results)
        elif args.action == "done":
            modified_count = mark_as_done(args.user.lower(), args.todo_id)
            if modified_count:
                display_success(
                    console, "Todo marked as done successfully", args.todo_id
                )
            else:
                display_error(console, "Todo not found", args.todo_id)
        else:
            display_error(console, f"Invalid action: {args.action}")
    except Exception as e:
        display_error(console, str(e))

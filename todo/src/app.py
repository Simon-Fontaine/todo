import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from rich.table import Table
from rich.console import Console
from todo.src.utils.panels import Color, create_panel
from datetime import datetime

load_dotenv()

mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
mongo_database = mongo_client["todo"]
console = Console()


def display_error(message: str):
    console.print(create_panel("Error", message, Color.DANGER))


def display_success(message: str):
    console.print(create_panel("Success", message, Color.SUCCESS))


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def add_todo(user: str, todo: str, priority: str, end_date: str | None):
    if end_date and not validate_date(end_date):
        display_error("Invalid date format. Use DD/MM/YYYY")
        return

    try:
        result = mongo_database[user].insert_one(
            {"todo": todo, "priority": priority, "end_date": end_date, "done": False}
        )
        display_success(f"Todo added successfully (id: {result.inserted_id})")
    except Exception as e:
        display_error(f"Failed to add todo: {str(e)}")


def delete_todo(user: str, todo_id: str):
    try:
        result = mongo_database[user].delete_one({"_id": ObjectId(todo_id)})
        if result.deleted_count == 0:
            display_error(f"Todo with id {todo_id} not found")
        else:
            display_success(f"Todo with id {todo_id} deleted successfully")
    except Exception as e:
        display_error(f"Failed to delete todo: {str(e)}")


def list_todo(user: str, sort: bool = False, filter: str | None = None):
    try:
        results = mongo_database[user].find({"priority": filter} if filter else {})
        table = Table(
            header_style="bold bright_white",
            min_width=60,
        )
        table.add_column("Todo", style="yellow")
        table.add_column("Priority", style="white")
        table.add_column("End Date", style="white")
        table.add_column("Done", style="white")
        table.add_column("ID", style="bright_black")

        if sort:
            results = results.sort("end_date", pymongo.ASCENDING)

        for todo in results:
            table.add_row(
                todo["todo"],
                todo["priority"],
                todo["end_date"],
                str(todo["done"]),
                str(todo["_id"]),
            )
        console.print(table)
    except Exception as e:
        display_error(f"Failed to list todos: {str(e)}")


def mark_todo_as_done(user: str, todo_id: str):
    try:
        result = mongo_database[user].update_one(
            {"_id": ObjectId(todo_id)}, {"$set": {"done": True}}
        )
        if result.modified_count == 0:
            display_error(f"Todo with id {todo_id} not found")
        else:
            display_success(f"Todo with id {todo_id} marked as done successfully")
    except Exception as e:
        display_error(f"Failed to mark todo as done: {str(e)}")


def app(args):
    if args.action == "add":
        add_todo(args.user, args.todo, args.priority, args.end_date)
    elif args.action == "delete":
        delete_todo(args.user, args.todo_id)
    elif args.action == "list":
        list_todo(args.user, args.sort, args.filter)
    elif args.action == "done":
        mark_todo_as_done(args.user, args.todo_id)
    else:
        display_error("Invalid action")

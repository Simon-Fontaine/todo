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

# TODO: faire une classe pour les todo avec des méthodes pour les manipuler
# TODO: créé des fonctions qui renvoient les todos modifiés pour les afficher
# TODO: plus facile pour les tests


def display_error(message: str = "An error occurred"):
    """Display an error message in a panel

    Parameters
    ----------
    message : str, optional
        The message to display in the panel, by default "An error occurred"
    """
    console.print(create_panel("Error", message, Color.DANGER))


def display_success(message: str = "Operation successful"):
    """Display a success message in a panel

    Parameters
    ----------
    message : str, optional
        The message to display in the panel, by default "Operation successful"
    """
    console.print(create_panel("Success", message, Color.SUCCESS))


def validate_date(date_str: str) -> bool:
    """Validate a date string

    Parameters
    ----------
    date_str : str
        The date string to validate

    Returns
    -------
    bool
        Whether the date is valid or not
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def add_todo(user: str, todo: str, priority: str, end_date: str | None):
    """Add a todo to the database

    Parameters
    ----------
    user : str
        The user to add the todo for
    todo : str
        The todo to add
    priority : str
        The priority of the todo
    end_date : str | None
        The end date of the todo
    """
    if end_date and not validate_date(end_date):
        return display_error("Invalid date format. Use YYYY-MM-DD")

    try:
        result = mongo_database[user].insert_one(
            {"todo": todo, "priority": priority, "end_date": end_date, "done": False}
        )
        display_success(f"Todo added successfully (id: {result.inserted_id})")
    except Exception as e:
        display_error(f"Failed to add todo: {str(e)}")


def delete_todo(user: str, todo_id: str):
    """Delete a todo from the database

    Parameters
    ----------
    user : str
        The user to delete the todo from
    todo_id : str
        The id of the todo to delete
    """
    try:
        result = mongo_database[user].delete_one({"_id": ObjectId(todo_id)})
        if result.deleted_count == 0:
            display_error(f"Todo with id {todo_id} not found")
        else:
            display_success(f"Todo with id {todo_id} deleted successfully")
    except Exception as e:
        display_error(f"Failed to delete todo: {str(e)}")


def list_todos(user: str, sort: bool = False, filter: str | None = None):
    """List todos from the database

    Parameters
    ----------
    user : str
        The user to list the todos for
    sort : bool, optional
        Whether to sort the todos by date or not, by default False
    filter : str | None, optional
        Whether to filter the todos by priority or not, by default None
    """
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
                str(todo["todo"]),
                str(todo["priority"]),
                str(todo["end_date"]),
                str(todo["done"]),
                str(todo["_id"]),
            )
        console.print(table)
    except Exception as e:
        display_error(f"Failed to list todos: {str(e)}")


def mark_todo_as_done(user: str, todo_id: str):
    """Mark a todo as done in the database

    Parameters
    ----------
    user : str
        The user to mark the todo as done for
    todo_id : str
        The id of the todo to mark as done
    """
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
    """The main application function

    Parameters
    ----------
    args : argparse.Namespace
        The arguments passed to the application
    """
    if args.action == "add":
        add_todo(args.user, args.todo, args.priority, args.end_date)
    elif args.action == "delete":
        delete_todo(args.user, args.todo_id)
    elif args.action == "list":
        list_todos(args.user, args.sort, args.filter)
    elif args.action == "done":
        mark_todo_as_done(args.user, args.todo_id)
    else:
        display_error("Invalid action")

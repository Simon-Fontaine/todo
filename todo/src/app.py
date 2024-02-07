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


def drop_user_collection(user: str):
    """Drop a user collection from the database

    Parameters
    ----------
    user : str
        The user collection to drop
    """
    mongo_database[user].drop()


def validate_date(date_str: str) -> bool:
    """Validate a date string

    Parameters
    ----------
    date_str : str
        The date string to validate

    Returns
    -------
    bool
        Whether the date string is valid

    Raises
    ------
    ValueError
        If the date string is invalid
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD")


def add_todo(user: str, todo: str, priority: str, end_date: str = None) -> str:
    """Add a todo to the database

    Parameters
    ----------
    user : str
        The user to add the todo for
    todo : str
        The todo to add
    priority : str
        The priority of the todo
    end_date : str, optional
        The end date of the todo, by default None

    Returns
    -------
    str
        The ID of the inserted todo

    Raises
    ------
    Exception
        If the todo could not be added
    """
    try:
        if end_date:
            validate_date(end_date)
        result = mongo_database[user].insert_one(
            {"todo": todo, "priority": priority, "end_date": end_date, "done": False}
        )
        return str(result.inserted_id)
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        raise Exception(f"Failed to add todo: {str(e)}")


def delete_todo(user: str, todo_id: str) -> int:
    """Delete a todo from the database

    Parameters
    ----------
    user : str
        The user to delete the todo from
    todo_id : str
        The ID of the todo to delete

    Returns
    -------
    int
        The number of deleted todos

    Raises
    ------
    Exception
        If the todo could not be deleted
    """
    try:
        result = mongo_database[user].delete_one({"_id": ObjectId(todo_id)})
        return result.deleted_count
    except Exception as e:
        raise Exception(f"Failed to delete todo: {str(e)}")


def list_todos(user: str, sort: bool = False, priority: str = None):
    """List todos from the database

    Parameters
    ----------
    user : str
        The user to list the todos for
    sort : bool, optional
        Whether to sort the todos by date or not, by default False
    priority : str, optional
        The priority to filter the todos by, by default None

    Returns
    -------
    Cursor | None
        The results of the query

    Raises
    ------
    Exception
        If the todos could not be listed
    """
    try:
        results = mongo_database[user].find({"priority": priority} if priority else {})
        if sort:
            results = results.sort("end_date", pymongo.ASCENDING)
        return results
    except Exception as e:
        raise Exception(f"Failed to list todos: {str(e)}")


def mark_as_done(user: str, todo_id: str) -> int:
    """Mark a todo as done

    Parameters
    ----------
    user : str
        The user to mark the todo as done for
    todo_id : str
        The ID of the todo to mark as done

    Returns
    -------
    int
        The number of modified todos

    Raises
    ------
    Exception
        If the todo could not be marked as done
    """
    try:
        result = mongo_database[user].update_one(
            {"_id": ObjectId(todo_id)}, {"$set": {"done": True}}
        )
        return result.modified_count
    except Exception as e:
        raise Exception(f"Failed to mark todo as done: {str(e)}")


def display_error(message: str = "An error occurred"):
    """Display an error message

    Parameters
    ----------
    message : str, optional
        The error message to display, by default "An error occurred"

    Returns
    -------
    Panel
        The error message panel
    """
    return create_panel("Error", message, Color.DANGER)


def display_success(message: str = "Operation successful"):
    """Display a success message

    Parameters
    ----------
    message : str, optional
        The success message to display, by default "Operation successful"

    Returns
    -------
    Panel
        The success message panel
    """
    return create_panel("Success", message, Color.SUCCESS)


def display_table(results):
    """Display a table of todos

    Parameters
    ----------
    results : Cursor
        The results of the query
    """
    table = Table(header_style="bold bright_white", min_width=75)
    table.add_column("Todo", style="yellow")
    table.add_column("Priority", style="white")
    table.add_column("End Date", style="white")
    table.add_column("Done", style="white")
    table.add_column("ID", style="bright_black")

    for todo in results:
        table.add_row(
            str(todo["todo"]),
            str(todo["priority"]),
            str(todo["end_date"]),
            str(todo["done"]),
            str(todo["_id"]),
        )
    console.print(table)


def app(args):
    """Run the todo app

    Parameters
    ----------
    args : Namespace
        The command-line arguments
    """
    try:
        if args.action == "add":
            todo_id = add_todo(args.user, args.todo, args.priority, args.end_date)
            console.print(display_success(f"Todo added successfully (id: {todo_id})"))
        elif args.action == "delete":
            deleted_count = delete_todo(args.user, args.todo_id)
            if deleted_count:
                console.print(display_success("Todo deleted successfully"))
            else:
                console.print(display_error(f"Todo with id {args.todo_id} not found"))
        elif args.action == "list":
            results = list_todos(args.user, args.sort, args.priority)
            display_table(results)
        elif args.action == "done":
            modified_count = mark_as_done(args.user, args.todo_id)
            if modified_count:
                console.print(display_success("Todo marked as done successfully"))
            else:
                console.print(display_error(f"Todo with id {args.todo_id} not found"))
        else:
            console.print(display_error("Invalid action"))
    except Exception as e:
        console.print(display_error(str(e)))

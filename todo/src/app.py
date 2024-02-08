import json
import pymongo
from rich import box
from rich.padding import Padding
from bson.objectid import ObjectId
from rich.table import Table
from datetime import datetime


f = open("secrets.json")
data = json.load(f)
f.close()

mongo_client = pymongo.MongoClient(data["mongo_uri"])
mongo_database = mongo_client["todo"]


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


def display_error(console, message: str = "An error occurred", id: str = None):
    """Display an error message

    Parameters
    ----------
    console : Console
        The console to display the error on
    message : str, optional
        The error message, by default "An error occurred"
    id : str, optional
        The ID of the error, by default None
    """
    message = (
        f"[bold red][ERROR][/bold red] {message} [black](id: {id})[black]"
        if id
        else f"[bold red][ERROR][/bold red] {message}"
    )

    console.print(Padding(message, (1, 0, 1, 0)))


def display_success(console, message: str = "Operation successful", id: str = None):
    """Display a success message

    Parameters
    ----------
    console : Console
        The console to display the success message on
    message : str, optional
        The success message, by default "Operation successful"
    id : str, optional
        The ID of the success message, by default None
    """
    message = (
        f"[bold green][SUCCESS][/bold green] {message} [black](id: {id})[black]"
        if id
        else f"[bold green][SUCCESS][/bold green] {message}"
    )

    console.print(Padding(message, (1, 0, 1, 0)))


def display_table(console, results):
    """Display a table of todos

    Parameters
    ----------
    console : Console
        The console to display the table on
    results : Cursor
        The results to display in the table
    """
    results = list(results)

    done_todos = sum(1 for todo in results if todo["done"])

    num_results = len(results)
    completion_percentage = (
        round(done_todos / num_results * 100) if num_results != 0 else 0
    )

    table = Table(
        min_width=75,
        row_styles=["none"],
        border_style="yellow",
        header_style="bold magenta",
        footer_style="bold black",
        box=box.SIMPLE,
        show_footer=True,
    )
    table.add_column("End Date")
    table.add_column("Todo")
    table.add_column("Priority")
    table.add_column("Done", "Status")
    table.add_column(
        "ID", f"{completion_percentage} % Completed ( {done_todos} / {num_results} )"
    )

    for todo in results:
        done_style = "green" if todo["done"] else "red"
        table.add_row(
            str(todo["end_date"]),
            str(todo["todo"]),
            str(todo["priority"]),
            str(todo["done"]),
            str(todo["_id"]),
            style=done_style,
        )
    console.print(table)


def app(console, args):
    """The main application logic

    Parameters
    ----------
    console : Console
        The console to display messages on
    args : argparse.Namespace
        The parsed arguments
    """
    try:
        if args.action == "add":
            todo_id = add_todo(args.user, args.todo, args.priority, args.end_date)
            display_success(console, "Todo added successfully", todo_id)
        elif args.action == "delete":
            deleted_count = delete_todo(args.user, args.todo_id)
            if deleted_count:
                display_success(console, "Todo deleted successfully", args.todo_id)
            else:
                display_error(console, "Todo not found", args.todo_id)
        elif args.action == "list":
            results = list_todos(args.user, args.sort, args.priority)
            display_table(console, results)
        elif args.action == "done":
            modified_count = mark_as_done(args.user, args.todo_id)
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

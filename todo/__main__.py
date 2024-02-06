import argparse
from rich.console import Console
from importlib.metadata import version
from todo.src.utils.panels import Color, create_panel
from todo.src.app import app


def main():
    console = Console()
    parser = create_arg_parser()

    args = parser.parse_args()

    try:
        if args.version:
            display_version(console)
        elif args.action in ["add", "delete", "list", "done"]:
            console.print(args)
            app(args)
        else:
            console.print(parser.format_help())
    except argparse.ArgumentError as e:
        console.print(create_panel("Error", str(e), Color.DANGER))


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", help="show the version of todo", action="store_true"
    )

    sub_parsers = parser.add_subparsers(dest="action")

    # Add subparsers
    add_parser = sub_parsers.add_parser("add", help="add a new todo item to the list")
    add_parser.add_argument("user", metavar="user", help="the user to log in as")
    add_parser.add_argument(
        "todo", metavar="todo", help="the todo to do (surround with quotes)"
    )
    add_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="the priority of the todo (default: medium)",
    )
    add_parser.add_argument("--end-date", help="when does the todo ends (DD/MM/YYYY)")

    # Delete subparsers
    delete_parser = sub_parsers.add_parser(
        "delete", help="delete a todo item from the list"
    )
    delete_parser.add_argument("user", metavar="user", help="the user to log in as")
    delete_parser.add_argument("todo_id", type=str, help="the id of the todo to delete")

    # List subparsers
    list_parser = sub_parsers.add_parser("list", help="list all todos for a user")
    list_parser.add_argument("user", metavar="user", help="the user to log in as")
    list_parser.add_argument(
        "--sort", action="store_true", help="sort todos by end date"
    )
    list_parser.add_argument(
        "--filter", choices=["low", "medium", "high"], help="filter todos by priority"
    )

    # Done subparsers
    done_parser = sub_parsers.add_parser("done", help="mark a todo as done")
    done_parser.add_argument("user", metavar="user", help="the user to log in as")
    done_parser.add_argument(
        "todo_id", type=str, help="the id of the todo to mark as done"
    )

    return parser


def display_version(console):
    todo_version = version("todo")
    console.print(create_panel("Version", f"Current version: {todo_version}"))


if __name__ == "__main__":
    main()

import argparse
from rich.console import Console
from importlib.metadata import version
from todo.src.utils.panels import Color, create_panel


def print_version(console):
    todo_version = version("todo")
    console.print(create_panel("Version", f"Current version: {todo_version}"))


def print_error(console, message):
    console.print(create_panel("Error", message, Color.DANGER))


def print_user(console, user):
    console.print(create_panel("User", f"Logged in as: {user}", Color.SUCCESS))


def main():
    console = Console()
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", help="Specify the user to log in as")
    parser.add_argument(
        "-v", "--version", help="Show the version of todo", action="store_true"
    )

    args = parser.parse_args()

    if args.version:
        print_version(console)
    else:
        if args.user is None:
            print_error(
                console,
                """You haven't provided the user to log in.
Example: py main.py --user example@todo.app""",
            )
        else:
            print_user(console, args.user)


if __name__ == "__main__":
    main()

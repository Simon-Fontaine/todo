import argparse
from rich.console import Console
from importlib.metadata import version
from todo.src.utils.panels import Color, create_panel
from todo.src.app import Action, app


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="Specify the user to log in as")
    parser.add_argument(
        "-a",
        "--action",
        choices=[a.name.lower() for a in Action],
        help="Specify the action to perform",
    )
    parser.add_argument(
        "-v", "--version", help="Show the version of todo", action="store_true"
    )
    return parser.parse_args()


def display_error(console: Console, message: str):
    console.print(create_panel("Error", message, Color.DANGER))


def main():
    console = Console()
    args = parse_arguments()

    if args.version:
        todo_version = version("todo")
        console.print(create_panel("Version", f"Current version: {todo_version}"))
    else:
        if args.user is None:
            display_error(
                console,
                """You haven't provided the user to log in.
Example: py main.py --user example_user""",
            )
        elif args.action is None:
            display_error(
                console,
                """You haven't provided the action to perform.
Example: py main.py --user example_user --action list""",
            )
        else:
            try:
                action = Action[args.action.upper()]
                app(args.user, action)
            except KeyError:
                display_error(
                    console,
                    """You have provided an invalid action.
Example: py main.py --user example_user --action list""",
                )


if __name__ == "__main__":
    main()

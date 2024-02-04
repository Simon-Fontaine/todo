import argparse
from importlib.metadata import version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", help="show the version of todo", action="store_true"
    )
    args = parser.parse_args()

    if args.version:
        ver = version("todo")
        print(f"todo - {ver}")
    else:
        # TODO: Add the actual code here
        print("Hello, World!")


if __name__ == "__main__":
    main()

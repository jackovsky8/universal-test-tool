"""CLI interface for test_tool project.
"""
from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig
from os import getcwd

from test_tool.base import run_tests


def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m test_tool` and `$ test_tool `.

    This is the program's entry point.
    """
    parser = ArgumentParser(
        prog="Test-Tool",
        description="This programm is a tool for running tests.",
        epilog="universal-test-tool Copyright (C) 2023 jackovsky8",
    )

    parser.add_argument(
        "-p",
        "--project",
        action="store",
        help="The path to the project.",
        default=getcwd(),
    )

    parser.add_argument(
        "-ca",
        "--calls",
        action="store",
        help="The filename of the calls configuration.",
        default="calls.yaml",
    )

    parser.add_argument(
        "-d",
        "--data",
        action="store",
        help="The filename of the data configuration.",
        default="data.yaml",
    )

    parser.add_argument(
        "-X", "--debug", action="store_true", help="Activate debugging."
    )

    args = parser.parse_args()

    if args.debug:
        basicConfig(
            level=DEBUG, format="%(asctime)s | %(levelname)s | %(message)s "
        )
    else:
        basicConfig(
            level=INFO, format="%(asctime)s | %(levelname)s | %(message)s "
        )

    run_tests(args.project, args.calls, args.data)

if __name__ == "__main__":  # pragma: no cover
    main()

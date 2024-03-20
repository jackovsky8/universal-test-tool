"""
CLI interface for test_tool project.

It is executed when the program is called from the command line.
"""
from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig
from os import getcwd
from pathlib import Path

from test_tool.base import run_tests

VERSION: str = "0.1.15"


def get_version_from_file() -> str:
    """
    Get the version of the program from the VERSION file.

    Returns:
    --------
    str
        The version of the program.
    """
    file = Path(__file__).parent.joinpath("VERSION")
    with open(file, "r", encoding="utf-8") as f:
        version = f.read().strip()
    return version


def main() -> None:  # pragma: no cover
    """
    The main function executes on commands:
    `python -m test_tool` and `$ test_tool `.

    This is the program's entry point.
    """
    parser = ArgumentParser(
        prog="test-tool",
        description="This programm runs tests configured by a yaml file.",
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
        "-c",
        "--continue_tests",
        action="store_true",
        help="Continue the tests even if one fails.",
        default=False,
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="Create a folder with the logs of the tests.",
        default="runs/%Y%m%d_%H%M%S",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Show the version of the program.",
    )

    parser.add_argument(
        "-X", "--debug", action="store_true", help="Activate debugging."
    )

    args = parser.parse_args()

    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    log_level = INFO

    if args.debug:
        log_level = DEBUG
    basicConfig(level=log_level, format=log_format)

    run_tests(
        args.project, args.calls, args.data, args.continue_tests, args.output
    )


if __name__ == "__main__":  # pragma: no cover
    main()

"""
Module for the suite plugin."""
from logging import getLogger
from pathlib import Path
from typing import TypedDict

from test_tool.base import run_tests

# Get the logger
test_tool_logger = getLogger("test-tool")


class SuiteCall(TypedDict):
    """
    This class represents an suite call.
    """

    project: str
    calls: str
    data: str
    continue_tests: bool
    output: str


# Define the default call
default_suite_call: SuiteCall = {
    "project": "",
    "calls": "calls.yaml",
    "data": "data.yaml",
    "continue_tests": False,
    "output": "runs/%Y%m%d_%H%M%S",
}


def make_suite_call(call: SuiteCall) -> None:
    """
    This function will be called to make the suite call.

    Parameters:
    ----------
    call: SuiteCall
        The call to make.
    """
    test_tool_logger.info(
        "Running suite call with project: %s, calls: %s, "
        + "data: %s, continue_tests: %s, output: %s",
        call["project"],
        call["calls"],
        call["data"],
        call["continue_tests"],
        call["output"],
    )

    run_tests(
        call["project"],
        call["calls"],
        call["data"],
        call["continue_tests"],
        call["output"],
    )


def augment_suite_call(call: SuiteCall, path: Path) -> None:
    """
    This function will be called to augment the suite call.

    Parameters:
    ----------
    call: SuiteCall
        The call to augment.
    path: Path
        The path to the project.
    """
    project_path = Path(call["project"])
    if not project_path.is_absolute():
        project_path = path.joinpath(project_path)

    call["project"] = project_path.as_posix()


def main() -> None:
    """
    This function will be called when the plugin is loaded.
    """
    print("test-tool-suite-plugin")

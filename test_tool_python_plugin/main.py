"""
Module for the python plugin.
"""
from logging import error, info
from pathlib import Path
from typing import Any, Dict, TypedDict


class PythonCall(TypedDict):
    """
    This class represents an python call.
    """

    run: str


# Define the default call
default_python_call: PythonCall = {"run": "val='Hello World!'\nprint(val)"}


def print_function(val: str) -> None:
    """
    This function will be called to print the value.

    Parameters:
    ----------
    val: str
        The value to print
    """
    info("\t%s", val)


def make_python_call(
    call: PythonCall, data: Dict[str, Any]  # pylint: disable=unused-argument
) -> None:
    """
    This function will be called to make the python call.

    Parameters:
    ----------
    call: PythonCall
        The call to make
    data: Dict
        The data that was passed to the function
    """
    info("Making python call:")
    for line in call["run"].split("\n"):
        info("\t%s", line)

    # Run the python code
    info("Output:")

    # Add the data as global variable
    if "PYTHON_PLUGIN" not in data:
        data["PYTHON_PLUGIN"] = {}

    global_vars: Dict[str, Any] = {"PYTHON_PLUGIN": data["PYTHON_PLUGIN"]}
    # make sure stdout is taken to the logger
    global_vars["print"] = print_function

    # Call the code
    try:
        exec(call["run"], global_vars)  # pylint: disable=exec-used
    except Exception as e:
        error("Error during execution: %s", e)
        raise e


def augment_python_call(
    call: PythonCall,  # pylint: disable=unused-argument
    data: Dict,
    path: Path,  # pylint: disable=unused-argument
) -> None:
    """
    This function will be called before the function above.
    It can be used to augment the call.

    Parameters:
    ----------
    call: PythonCall
        The call to augment
    data: Dict
        The data that was passed to the function
    path: Path
        The path of the file that contains the call
    """


def main() -> None:
    """
    This function will be called when the plugin is loaded.
    """
    print("test-tool-python-plugin")

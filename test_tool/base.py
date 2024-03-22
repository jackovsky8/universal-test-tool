"""
test_tool base module.

This is the principal module of the test_tool project.
"""
import sys
from copy import deepcopy
from datetime import datetime
from importlib import import_module
from inspect import getfullargspec
from logging import DEBUG, INFO, FileHandler, Formatter, getLogger
from pathlib import Path
from traceback import print_exception
from types import FunctionType
from typing import Any, Callable, Dict, List, TypedDict

from yaml import YAMLError, safe_load

from test_tool import recursively_replace_variables

# Get the logger
test_tool_logger = getLogger("test-tool")


class CallType(TypedDict):
    """
    Call Type.
    """

    default_call: Dict[str, Any]
    augment_call: Callable
    make_call: Callable


class Call(TypedDict):
    """
    Call.
    """

    type: str
    call: Dict[str, Any]
    line: int


# Plugin Name Templates
PLUGIN_NAME_TEMPLATE: str = "test_tool_${plugin}_plugin"

# Plugin Template
PLUGIN_TEMPLATE: Dict[str, str] = {
    "default_call": "default_${plugin}_call",
    "augment_call": "augment_${plugin}_call",
    "make_call": "make_${plugin}_call",
}

PLUGIN_COMPONENT_TYPES: Dict[str, type] = {
    "default_call": dict,
    "augment_call": FunctionType,
    "make_call": FunctionType,
}


def import_plugin(plugin: str, loaded_call_types: Dict[str, CallType]) -> bool:
    """
    Dynamically import the specified plugin as a module.

    Parameters
    ----------
    plugin : str
        Name of the plugin.

    Returns
    -------
    bool
        True if the plugin was loaded successfully, False otherwise.
    """
    try:
        plugin_module = import_module(
            PLUGIN_NAME_TEMPLATE.replace("${plugin}", plugin.lower())
        )
    except ModuleNotFoundError:
        test_tool_logger.error(
            "Plugin %s not found, try to install it with pip install"
            + " test_tool_%s_plugin",
            plugin,
            plugin.lower(),
        )
        return False

    # Create a dict for the loaded plugin
    loaded_plugin: CallType = {
        "default_call": {},
        "augment_call": lambda *args, **kwargs: None,
        "make_call": lambda *args, **kwargs: None,
    }

    # Load the components from the plugin
    to_load: Dict[str, str] = {
        key: val.replace("${plugin}", plugin.lower())
        for key, val in PLUGIN_TEMPLATE.items()
    }
    for key, component in to_load.items():
        try:
            loaded_plugin[key] = getattr(  # type: ignore
                plugin_module, component
            )
        except AttributeError:
            # We can ignore this error, because default value is set
            pass
        if not isinstance(
            loaded_plugin[key], PLUGIN_COMPONENT_TYPES[key]  # type: ignore
        ):
            msg: str = (
                f"Module test_tool_{plugin.lower()}_plugin is not a valid "
                + f"plugin, {component} is not a {PLUGIN_COMPONENT_TYPES[key]}"
            )
            test_tool_logger.error(msg)
            raise AttributeError(msg)

    loaded_call_types[plugin] = loaded_plugin
    return True


def make_all_calls(
    calls: List[Call],
    data: Dict[str, Any],
    path: Path,  # pylint: disable=unused-argument
    continue_on_failure: bool,
) -> int:
    """
    Make all calls.

    Parameters
    ----------
    calls : List[Call]
        List of calls.
    data : Dict[str, Any]
        Data to use for the calls.
    path : Path
        Path to the project.
    continue_on_failure : bool
        Continue tests on error.

    Returns
    -------
    int
        Number of errors.
    """
    errors: int = 0
    # Loaded Plugins
    loaded_call_types: Dict[str, CallType] = dict()

    # Make the calls and check the response
    for idx, test in enumerate(calls):
        # Stopping on first error
        if errors > 0 and not continue_on_failure:
            test_tool_logger.error("Stopping on first error")
            break

        if "type" not in test:
            test_tool_logger.error(
                "No type specified for test from line %s using assert plugin",
                test["line"],
            )
            test["type"] = "ASSERT"

        # Atomic error handling
        error = False

        # Make sure the plugin is loaded
        if not error:
            if not test["type"] in loaded_call_types:
                test_tool_logger.debug(
                    "Loading plugin for call type %s", test["type"]
                )
                if not import_plugin(test["type"], loaded_call_types):
                    test_tool_logger.error(
                        "%s call is not supported", test["type"]
                    )
                    errors += 1
                    error = True

        # Merge the default call with the call from the config
        if not error:
            default_call = deepcopy(
                loaded_call_types[test["type"]]["default_call"]
            )
            try:
                call = {**default_call, **test["call"]}
            except KeyError:
                call = default_call

        # Recursivly replace variables in call with data
        if not error:
            try:
                recursively_replace_variables(call, data)
            except (KeyError, ValueError) as e:
                # if debug is enabled print the exception
                if test_tool_logger.getEffectiveLevel() == DEBUG:
                    print_exception(type(e), e, e.__traceback__)
                errors += 1
                error = True

        # Call the funktion
        if not error:
            try:
                test_tool_logger.info(
                    "Make call %s in %s plugin.", idx + 1, test["type"]
                )
                # Augment the call with the data from the config
                args: List[str] = getfullargspec(
                    loaded_call_types[test["type"]]["augment_call"]
                )[0]
                call_args: Dict[str, Any] = {}
                allowed_args: List[str] = ["call", "data", "path"]
                for arg in args:
                    if arg in allowed_args:
                        call_args[arg] = locals()[arg]
                loaded_call_types[test["type"]]["augment_call"](**call_args)
                # Make the call
                args = getfullargspec(
                    loaded_call_types[test["type"]]["make_call"]
                )[0]
                call_args = {}
                allowed_args = ["call", "data"]
                for arg in args:
                    if arg in allowed_args:
                        call_args[arg] = locals()[arg]
                loaded_call_types[test["type"]]["make_call"](**call_args)
            except AssertionError as e:
                test_tool_logger.error(
                    "Assertion error for test from line %s: %s",
                    test["line"],
                    e,
                )
                errors += 1
                error = True
            except Exception as e:  # pylint: disable=broad-except
                test_tool_logger.error(
                    'Exception "%s" occured for test from line %s '
                    + "(This might be a problem with the plugin or config).",
                    e,
                    test["line"],
                )
                # if debug is enabled print the exception
                if test_tool_logger.getEffectiveLevel() == DEBUG:
                    print_exception(type(e), e, e.__traceback__)
                errors += 1
                error = True

    return errors


def load_config_yaml(path: Path, add_line_numbers: bool = False) -> Any:
    """
    Load a yaml config file.

    Parameters
    ----------
    path : Path
        Path to the file.
    add_line_numbers : bool, optional
        Add line numbers to the loaded data,
        if the data is a list, by default False

    Returns
    -------
    Dict[str, Any]
        The loaded config.
    """
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    try:
        data = safe_load(content)
    except YAMLError as e:
        test_tool_logger.error(e)
        sys.exit(1)

    if add_line_numbers and isinstance(data, list):
        line_numbers = []
        # Every call starts with "- call: or - type:"
        intendation = 0
        for idx, line in enumerate(content.split("\n")):
            if "- call:" in line or "- type:" in line:
                # Count characters before "- call:"
                if idx > 0 and len(line) - len(line.lstrip()) == intendation:
                    line_numbers.append(idx + 1)
                elif idx == 0:
                    intendation = len(line) - len(line.lstrip())
                    line_numbers.append(idx + 1)

        for idx, element in enumerate(data):
            if isinstance(element, dict):
                element["line"] = line_numbers[idx]

    return data


def run_tests(
    project_path_str: str,
    calls_path_str: str,
    data_path_str: str,
    continue_on_failure: bool,
    output: str,
) -> None:
    """
    Run the tests.

    Parameters
    ----------
    project_path_str : str
        Path to the project.
    calls_path_str : str
        Path to the calls config.
    data_path_str : str
        Path to the data config.
    continue_on_failure : bool
        Continue tests on error.
    output : str
        Path to the output folder.
    """
    project_path: Path = Path(project_path_str)
    test_tool_logger.info(
        "Running tests for project %s", project_path.as_posix()
    )

    calls_path: Path = project_path.joinpath(calls_path_str)
    test_tool_logger.info("Calls: %s", calls_path.relative_to(project_path))

    data_path: Path = project_path.joinpath(data_path_str)
    if data_path.exists():
        test_tool_logger.info("Data: %s", data_path.relative_to(project_path))

        # Load the data
        data: Dict[str, Any] = load_config_yaml(data_path)
        if data is None:
            data = {}
        for key, value in data.items():
            test_tool_logger.debug("Loaded %s for %s", value, key)
    else:
        test_tool_logger.info("No data file found, using empty data dict.")
        data = {}

    # Set the project path in the data
    data["PROJECT_PATH"] = project_path.as_posix()

    # Check if output is set
    if output:
        # Create a string from datetime in format YYYYMMDD_HHMMSS
        now_str = datetime.now().strftime(output)
        output_path: Path = project_path.joinpath(now_str)
        test_tool_logger.debug(
            "Create output folder %s", output_path.relative_to(project_path)
        )
        output_path.mkdir(parents=True, exist_ok=True)

        # Set the output path in the data
        data["OUTPUT_PATH"] = output_path.as_posix()

        # Add Handler to logger to write to file
        fh = FileHandler(output_path.joinpath("run.log"))
        fh.setLevel(INFO)
        fh.setFormatter(
            Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        test_tool_logger.addHandler(fh)

    # Load the calls
    calls: List[Call] = load_config_yaml(calls_path, True)
    errors = make_all_calls(calls, data, project_path, continue_on_failure)

    if errors == 0:
        test_tool_logger.info("Everything OK")
    else:
        test_tool_logger.error(
            "There occured %s test_tool_logger.errors while testing,"
            + "please check the logs",
            errors,
        )
        sys.exit(1)

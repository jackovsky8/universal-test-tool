"""
test_tool base module.

This is the principal module of the test_tool project.
"""
import sys
from copy import deepcopy
from datetime import datetime
from importlib import import_module
from logging import DEBUG, INFO, FileHandler, Formatter, getLogger
from pathlib import Path
from traceback import print_exception
from types import FunctionType
from typing import Any, Callable, Dict, List, Optional, TypedDict
from re import findall, search, sub

from yaml import YAMLError, safe_load

test_tool_logger = getLogger("test-tool")


class CallType(TypedDict):
    """
    Call Type.
    """

    default_call: Dict[str, Any]
    augment_call: Callable
    make_call: Callable


# Loaded Plugins
LOADED_CALL_TYPES: Dict[str, CallType] = dict()


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


def import_plugin(plugin: str) -> bool:
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
        "augment_call": lambda x: x,
        "make_call": lambda x: x,
    }

    # Load the components from the plugin
    to_load: Dict[str, str] = {
        key: val.replace("${plugin}", plugin.lower())
        for key, val in PLUGIN_TEMPLATE.items()
    }
    try:
        for key, component in to_load.items():
            loaded_plugin[key] = getattr(  # type: ignore
                plugin_module, component
            )
            if not isinstance(
                loaded_plugin[key], PLUGIN_COMPONENT_TYPES[key]  # type: ignore
            ):
                test_tool_logger.error(
                    "Module test_tool_%s_plugin is not a valid plugin, %s is"
                    + " not a %s",
                    plugin.lower(),
                    component,
                    PLUGIN_COMPONENT_TYPES[key],
                )
                return False
    except AttributeError:
        test_tool_logger.error(
            "Module test_tool_%s_plugin is not a valid plugin, missing a"
            + " component.",
            plugin.lower(),
        )
        return False

    LOADED_CALL_TYPES[plugin] = loaded_plugin
    return True


def replace_string_variables(
    to_change: str, data: Dict[str, Any]
) -> Optional[str]:
    """
    Replace variables in a string.

    Parameters
    ----------
    to_change : str
        String to change.
    data : Dict[str, Any]
        Data to use for the changes.

    Returns
    -------
    Optional[str]
        The changed string if it was changed, None otherwise.
    """
    changed: Any = to_change

    # Find all variables in the string. Variables are defined as {{foo.bar[0]}}
    pattern = r"{{[a-zA-Z0-9\_\-\.\[\]]+}}"
    variables = findall(pattern, changed)
    # Replace the variables with the data if they are in the data, otherwise leave them
    for variable in variables:
        # Remove ${ and }
        var = variable[2:-2]
        # Split for objects
        keys = var.split(".")
        # Check if path is list
        list_pattern = r"\[(\d+)\]$"
        # Keep track for logging
        log_path = "data"
        # Get the value
        value: Dict[str, Any] | List[Any] | str = data
        for key in keys:
            is_list = search(list_pattern, key)
            if is_list:
                list_key = int(is_list.group(1))
                key = sub(list_pattern, "", key)
            try:
                value = value[key]
            except KeyError:
                test_tool_logger.error(
                    "Key %s not found in %s", key, log_path
                )
                value = variable
                break
            log_path += "." + key
            if is_list:
                try:
                    value = value[list_key]
                except IndexError:
                    test_tool_logger.error(
                        "Index %s not found in list %s", list_key, log_path
                    )
                    value = variable
                    break
                log_path += f"[{list_key}]"

        if changed == variable:
            changed = value
        else:
            changed = changed.replace(variable, str(value))

    if changed != to_change:
        test_tool_logger.debug("Changed value %s to %s.", to_change, changed)
        return changed

    return None


def recursively_replace_variables(
    to_change: Dict[str, Any], data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Recursively replace variables in a dict.

    Parameters
    ----------
    to_change : Dict[str, Any]
        Dict to change.
    data : Dict[str, Any]
        Data to use for the changes.

    Returns
    -------
    Dict[str, Any]
        The changed dict.
    """
    changed: bool = False
    for key, value in to_change.items():
        test_tool_logger.debug("%s: %s", key, value)
        changed = False
        changed_iteration: bool = True
        while changed_iteration:
            changed_iteration = False
            if isinstance(to_change[key], dict):
                changed_iteration = (
                    recursively_replace_variables(to_change[key], data) is not None
                )
            elif isinstance(to_change[key], list):
                for idx, val in enumerate(to_change[key]):
                    if isinstance(val, dict):
                        new_val = recursively_replace_variables(val, data)
                        if new_val:
                            changed_iteration = True
                            to_change[key][idx] = new_val
                    elif isinstance(val, str):
                        new_value = replace_string_variables(val, data)
                        if new_value:
                            changed_iteration = True
                            to_change[key][idx] = new_val
            elif isinstance(to_change[key], str):
                new_value = replace_string_variables(to_change[key], data)
                if new_value is not None:
                    changed_iteration = True
                    to_change[key] = new_value

        if changed_iteration:
            changed = True

    if changed:
        return to_change
    else:
        return None


def make_all_calls(
    calls: List[Call], data: Dict[str, Any], path: Path, continue_tests
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
    continue_tests : bool
        Continue tests on error.

    Returns
    -------
    int
        Number of errors.
    """
    errors: int = 0

    # Make the calls and check the response
    for idx, test in enumerate(calls):
        # Check if call type is defined
        try:
            test["type"]
        except KeyError:
            test_tool_logger.debug("No call type defined, using default: REST")
            test["type"] = "REST"

        # Determine if the call type is loaded
        try:
            LOADED_CALL_TYPES[test["type"]]
        except KeyError:
            # Module is not loaded yet, load it
            test_tool_logger.debug(
                "Loading plugin for call type %s", test["type"]
            )
            if not import_plugin(test["type"]):
                test_tool_logger.error(
                    "%s call is not supported", test["type"]
                )
                errors += 1
                continue

        # Merge the default call with the call from the config
        default_call = deepcopy(
            LOADED_CALL_TYPES[test["type"]]["default_call"]
        )
        try:
            call = {**default_call, **test["call"]}
        except KeyError as e:
            if "'call'" == str(e):
                call = default_call
            else:
                test_tool_logger.error("Key %s not found in call", e)
                errors += 1
                continue

        # Recursivly replace variables in call with data
        recursively_replace_variables(call, data)

        # Call the funktion
        try:
            test_tool_logger.info(
                "Make call %s in %s plugin.", idx + 1, test["type"]
            )
            # Augment the call with the data from the config
            LOADED_CALL_TYPES[test["type"]]["augment_call"](call, data, path)
            # Make the call
            LOADED_CALL_TYPES[test["type"]]["make_call"](call, data)
        except AssertionError as e:
            test_tool_logger.error(
                "Assertion error for test from line %s: %s", test["line"], e
            )
            errors += 1
        except Exception as e:  # pylint: disable=broad-except
            test_tool_logger.error(
                'Exception "%s" occured for test from line %s '
                + "(This might be a problem with the plugin or config).",
                e,
                test["line"],
            )
            # if debug:
            if test_tool_logger.getEffectiveLevel() == DEBUG:
                print_exception(type(e), e, e.__traceback__)
            errors += 1

        if errors > 0 and not continue_tests:
            test_tool_logger.error("Stopping on first error")
            break

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
    continue_tests: bool,
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
    continue_tests : bool
        Continue tests on error.
    output : str
        Path to the output folder.
    """
    project_path: Path = Path(project_path_str)
    calls_path: Path = project_path.joinpath(calls_path_str)
    data_path: Path = project_path.joinpath(data_path_str)

    test_tool_logger.info(
        "Running tests for project %s", project_path.as_posix()
    )
    test_tool_logger.debug("Calls: %s", calls_path.relative_to(project_path))
    test_tool_logger.debug("Data: %s", data_path.relative_to(project_path))

    # Load the data
    data: Dict[str, Any] = load_config_yaml(data_path)
    if data is None:
        data = {}
    for key, value in data.items():
        test_tool_logger.debug("Loaded %s for %s", value, key)

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
    errors = make_all_calls(calls, data, project_path, continue_tests)

    if errors == 0:
        test_tool_logger.info("Everything OK")
        sys.exit(0)
    else:
        test_tool_logger.error(
            "There occured %s test_tool_logger.errors while testing,"
            + "please check the logs",
            errors,
        )
        sys.exit(1)

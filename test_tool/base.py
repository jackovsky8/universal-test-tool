"""
test_tool base module.

This is the principal module of the test_tool project.
"""
from copy import deepcopy
from enum import Enum
from importlib import import_module
from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Callable
from types import FunctionType

from yaml import YAMLError, safe_load


# Call Type
class CallType(TypedDict):
    default_call: Dict[str, Any]
    augment_call: Callable
    make_call: Callable

# Loaded Plugins
LOADED_CALL_TYPES: Dict[str, CallType] = dict()

# Call
class Call(TypedDict):
    type: str
    call: Dict[str, Any]

# Plugin Name Templates
PLUGIN_NAME_TEMPLATE: str = "test_tool_${plugin}_plugin"

# Plugin Template
PLUGIN_TEMPLATE: List[str] = [
    "default_${plugin}_call",
    "augment_${plugin}_call",
    "make_${plugin}_call",
]

PLUGIN_COMPONENT_TYPES: Dict[str, type] = {
    "default_call": dict,
    "augment_call": FunctionType,
    "make_call": FunctionType,
}

def import_plugin(plugin: str) -> bool:
    # Dynamically import the specified components from the module
    try:
        plugin_module = import_module(PLUGIN_NAME_TEMPLATE.replace("${plugin}", plugin.lower()))
    except ModuleNotFoundError as e:
        error(f"Plugin {plugin} not found, try to install it with pip install test_tool_{plugin.lower()}_plugin")
        return False

    # Create a dict for the loaded plugin
    loaded_plugin: Dict[str, Any] = dict()

    # Load the components from the plugin
    to_load = [el.replace("${plugin}", plugin.lower()) for el in PLUGIN_TEMPLATE]
    try:
        for component in to_load:
            key: str = component.replace(f"{plugin.lower()}_", "")
            loaded_plugin[key] = getattr(plugin_module, component)
            if type(loaded_plugin[key]) != PLUGIN_COMPONENT_TYPES[key]:
                error(f"Module test_tool_{plugin.lower()}_plugin is not a valid plugin, {component} is not a {PLUGIN_COMPONENT_TYPES[key]}")
                return False
    except AttributeError as e:
        error(f"Module test_tool_{plugin.lower()}_plugin is not a valid plugin, missing a component.")
        return False

    LOADED_CALL_TYPES[plugin] = loaded_plugin
    return True

def replace_string_variables(to_change : str, data: Dict[str, Any]) -> str:
    changed: str = to_change
    for var, val in data.items():
        # We only want to replace with strings
        if type(val) is not str:
            continue

        # The string we want to search for
        origin: str = "${" + var + "}"

        # Check if the string contains the origin
        changed = changed.replace(origin, val)

    if changed != to_change:
        debug(f"Changed value {to_change} to {changed}.")
        return changed
    
    return None

def recursively_replace_variables(to_change : Dict[str, Any], data: Dict[str, Any]) -> None:
    for key, value in to_change.items():
        debug(f"{key}: {value}")
        changed: bool = False
        changed_iteration: bool = True
        while changed_iteration:
            changed_iteration = False
            if type(to_change[key]) is dict:
                changed_iteration = recursively_replace_variables(value, data)
            elif type(to_change[key]) is list:
                for idx, val in enumerate(to_change[key]):
                    if type(val) is dict:
                        new_val = recursively_replace_variables(val, data)
                        if new_val:
                            changed_iteration = True
                            to_change[key][idx] = new_val
                    elif type(val) is str:
                        new_value = replace_string_variables(to_change[key], data)
                        if new_value:
                            changed_iteration = True
                            to_change[key][idx] = new_val
            elif type(to_change[key]) is str:
                new_value = replace_string_variables(to_change[key], data)
                if new_value:
                    changed_iteration = True
                    to_change[key] = new_value

        if changed_iteration:
            changed = True

    if changed:
        return to_change

def make_all_calls(calls: List[Call], data: Dict[str, Any], path: Path) -> int:
    errors = 0

    # Make the calls and check the response
    for idx, test in enumerate(calls):
        # Check if call type is defined
        try:
            test["type"]
        except KeyError:
            debug("No call type defined, using default: REST")
            test["type"] = "REST"

        # Determine if the call type is loaded
        try:
            LOADED_CALL_TYPES[test["type"]]
        except KeyError as e:
            # Module is not loaded yet, load it
            debug(f"Loading plugin for call type {test['type']}")
            if not import_plugin(test["type"]):
                error(f'{test["type"]} call is not supported')
                errors += 1
                continue

        # Merge the default call with the call from the config
        default_call = deepcopy(LOADED_CALL_TYPES[test["type"]]["default_call"])
        try:
            call = {**default_call, **test["call"]}
        except KeyError as e:
            if "'call'" == str(e):
                call = default_call
            else:
                error(f"Key {e} not found in call")
                errors += 1
                continue

        # Recursivly replace variables in call with data
        recursively_replace_variables(call, data)

        # Augment the call with the data from the config
        LOADED_CALL_TYPES[test["type"]]["augment_call"](call, data, path)

        # Call the funktion
        try:
            info(f'Make call {idx + 1} in {test["type"]} plugin.')
            LOADED_CALL_TYPES[test["type"]]["make_call"](call, data)
            pass
        except AssertionError:
            errors += 1

    return errors


def load_config_yaml(config: Path):
    with open(config, "r") as stream:
        try:
            return safe_load(stream)
        except YAMLError as exc:
            error(exc)
            exit(1)


def run_tests(
    project_path_str: str, calls_path_str: str, data_path_str: str
) -> None:
    project_path: Path = Path(project_path_str)
    calls_path: Path = project_path.joinpath(calls_path_str)
    data_path: Path = project_path.joinpath(data_path_str)

    info(f"Running tests for project {project_path.as_posix()}")
    debug(f"Load calls from {calls_path.as_posix()}")
    debug(f"Load data from {data_path.as_posix()}")

    # Load the data
    data = load_config_yaml(data_path)
    if data is None:
        data = {}
    for key, value in data.items():
        debug(f"Loaded {value} for {key}")

    # Load the calls
    calls = load_config_yaml(calls_path)
    errors = make_all_calls(calls, data, project_path)

    if errors == 0:
        info("Everything OK")
    else:
        error(
            "There occured {} errors while testing, please check the logs".format(
                errors
            )
        )

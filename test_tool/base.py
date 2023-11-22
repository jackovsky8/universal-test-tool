"""
test_tool base module.

This is the principal module of the test_tool project.
here you put your main classes and objects.
"""
from copy import deepcopy
from enum import Enum
from importlib import import_module
from logging import debug, error, info
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from yaml import YAMLError, safe_load

NAME = "test_tool"


class DynamicEnum:
    def __init__(self, *enum_values):
        for value in enum_values:
            setattr(self, value, value)


plugin_path: Path = Path(__file__).parent.parent.joinpath("plugins")
plugin_files: List[Path] = plugin_path.glob("*_plugin.py")
call_types: List[str] = [
    file.name.replace("_plugin.py", "") for file in plugin_files
]

CallType = Enum("CallType", [call_type.upper() for call_type in call_types])

# Import all plugins
components_from_plugin = [
    "default_${plugin}_call",
    "augment_${plugin}_call",
    "make_${plugin}_call",
]

# Dynamically import the specified components from the module
plugin_module = import_module("plugins")
plugins: Dict[str, Any] = dict()
for plugin in call_types:
    components: List = [
        component.replace("${plugin}", plugin)
        for component in components_from_plugin
    ]
    imported_components = {
        component.replace(f"{plugin}_", ""): getattr(plugin_module, component)
        for component in components
    }
    plugins[CallType[plugin.upper()]] = imported_components


class Call(TypedDict):
    type: CallType
    call: Dict[str, Any]


def make_all_calls(calls: List[Call], data: Dict[str, Any], path: Path) -> int:
    errors = 0

    # Make the calls and check the response
    for idx, test in enumerate(calls):
        # Determin the call type, default is REST
        try:
            test["type"] = CallType[test["type"]]  # type: ignore
        except KeyError as e:
            if "'type'" == str(e):
                test["type"] = CallType["REST"]
            else:
                error(f'{test["type"]} call is not supported')
                errors += 1
                continue

        # Merge the default call with the call from the config
        default_call = deepcopy(plugins[test["type"]]["default_call"])
        try:
            call = {**default_call, **test["call"]}
        except KeyError as e:
            if "'call'" == str(e):
                call = default_call
            else:
                error(f"Key {e} not found in call")
                errors += 1
                continue

        # Replace variables in call with data
        for key, value in call.items():
            debug(f"{key}: {value}")
            changed: bool = True
            while changed:
                changed = False
                if type(value) is str:
                    for var, val in data.items():
                        origin: str = "${" + var + "}"
                        changed = changed or (value.find(origin) >= 0)
                        value = value.replace(origin, val)
                    if changed:
                        debug(f"Changed value {key} to: {value}")
                        call[key] = value

        # Augment the call with the data from the config
        plugins[test["type"]]["augment_call"](call, data, path)

        # Call the funktion
        try:
            info(f'Make call {idx + 1} in {test["type"].name} plugin.')
            plugins[test["type"]]["make_call"](call, data)
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

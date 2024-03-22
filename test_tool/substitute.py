"""
This module contains the functions to substitute variables.
"""
from logging import getLogger
from re import findall, search, sub
from typing import Any, Callable, Dict, List, Optional

# Get the logger
test_tool_logger = getLogger("test-tool")

# Define the pipes
available_pipes: Dict[str, Callable] = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool,
    "round": round,
}


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
    pattern = r"{{[a-zA-Z0-9\_\-\.\[\]\|\:]+}}"
    variables = findall(pattern, changed)
    # Replace the variables with the data, if possible
    for variable in variables:
        # Remove {{ and }}
        var = variable[2:-2]
        # Remove spaces
        var = var.strip()
        # Split for pipes
        pipes = var.split("|")
        # Get the variable
        var = pipes[0]
        # Get the pipes
        pipes = pipes[1:]
        # Split for objects
        keys = var.split(".")
        # Check if path is list
        list_pattern = r"\[(-?\d+)\]$"
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
            except KeyError as e:
                test_tool_logger.error("Key %s not found in %s", key, log_path)
                raise KeyError(f"Key {key} not found in {log_path}") from e
            log_path += "." + key
            if is_list:
                try:
                    value = value[list_key]
                except IndexError as e:
                    test_tool_logger.error(
                        "Index %s not found in list %s", list_key, log_path
                    )
                    raise IndexError(
                        f"Index {list_key} not found in list {log_path}"
                    ) from e
                log_path += f"[{list_key}]"

        if changed == variable:
            for pipe in pipes:
                # Get arguments
                pipe = pipe.split(":")
                arguments = pipe[1:]
                for idx, argument in enumerate(arguments):
                    if isinstance(argument, str):
                        try:
                            arguments[idx] = int(argument)
                            argument = arguments[idx]
                        except ValueError:
                            pass
                    if isinstance(argument, str):
                        try:
                            arguments[idx] = float(argument)
                            argument = arguments[idx]
                        except ValueError:
                            pass
                    # remove the quotes
                    if isinstance(argument, str):
                        if argument[0] == argument[-1] and argument[0] in [
                            "'",
                            '"',
                        ]:
                            arguments[idx] = argument[1:-1]
                            argument = arguments[idx]

                pipe = pipe[0]
                if pipe in available_pipes:
                    value = available_pipes[pipe](value, *arguments)
                else:
                    test_tool_logger.error(
                        "Pipe %s not found in available pipes", pipe
                    )
                    raise KeyError(f"Pipe {pipe} not found in available pipes")
            changed = value
        else:
            changed = changed.replace(variable, str(value))

    if changed != to_change:
        test_tool_logger.debug("Changed value %s to %s.", to_change, changed)
        return changed

    return None


def replace_list_variables(
    to_change: List[Any], data: Dict[str, Any]
) -> Optional[List[Any]]:
    """
    Replace variables in a list.

    Parameters
    ----------
    to_change : List[Any]
        List to change.
    data : Dict[str, Any]
        Data to use for the changes.

    Returns
    -------
    Optional[List[Any]]
        The changed list if it was changed, None otherwise.
    """
    changed: bool = False
    for idx, value in enumerate(to_change):
        if isinstance(value, str):
            new_string_value = replace_string_variables(value, data)
            if new_string_value is not None:
                changed = True
                to_change[idx] = new_string_value
        elif isinstance(value, dict):
            new_dict_value = recursively_replace_variables(value, data)
            if new_dict_value is not None:
                changed = True
                to_change[idx] = new_dict_value
        elif isinstance(value, list):
            new_list_value = replace_list_variables(value, data)
            if new_list_value is not None:
                changed = True
                to_change[idx] = new_list_value

    if changed:
        return to_change
    else:
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
                new_dict = recursively_replace_variables(to_change[key], data)
                if new_dict is not None:
                    changed_iteration = True
                    to_change[key] = new_dict
            elif isinstance(to_change[key], list):
                new_list = replace_list_variables(to_change[key], data)
                if new_list is not None:
                    changed_iteration = True
                    to_change[key] = new_list
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

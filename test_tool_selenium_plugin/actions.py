"""
This module contains the functions to get the arguments
"""
from enum import Enum
from logging import getLogger
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union

from test_tool_selenium_plugin.native import (get_native_argument,
                                              get_native_function)

__all__ = ["ArgumentType", "SeleniumAction", "get_arguments", "run_action"]

# Get the logger
test_tool_logger = getLogger("test-tool")

# Type definition for arguments
Arguments = List[Union[Dict[Any, Any], List[Any], str, int, float, bool]]


class ArgumentType(Enum):
    """
    Enum for the different argument types.
    """

    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    LIST = "list"
    DICTIONARY = "dictionary"
    EVAL = "eval"
    NATIVE = "native"
    ACTION = "action"


class SeleniumAction(TypedDict):
    """
    The structure of a Selenium action.
    """

    action: str
    args: Arguments
    actions: Optional[List["SeleniumAction"]]
    log: Optional[str]
    # Since 3.11
    # actions: NotRequired[List["SeleniumAction"]]
    # log: NotRequired[str]


def assert_equals(
    reference: Any, given: Any, message: str = "Values should equal:"
) -> None:
    """Assert that the given and reference values are equal."""
    assert (
        reference == given
    ), f"{message} Reference: {reference} Given: {given}"


def assert_not_equals(
    reference: Any, given: Any, message: str = "Values should not equal:"
) -> None:
    """Assert that the given and reference values are not equal."""
    assert (
        reference != given
    ), f"{message} Reference: {reference} Given: {given}"


def assert_true(given: Any, message: str = "Value should be true:") -> None:
    """Assert that the given value is true."""
    assert given, f"{message} Given: {given}"


def assert_false(given: Any, message: str = "Value should be false:") -> None:
    """Assert that the given value is false."""
    assert not given, f"{message} Given: {given}"


def assert_greater_than(
    reference: Any, given: Any, message: str = "Value should be greater than:"
) -> None:
    """Assert that the given value is greater than the reference value."""
    assert (
        reference > given
    ), f"{message} Reference: {reference} Given: {given}"


def assert_greater_than_or_equals(
    reference: Any,
    given: Any,
    message: str = "Value should be greater or equal than:",
) -> None:
    """Assert that the given value is greater than or equals the reference value."""
    assert (
        reference >= given
    ), f"{message} Reference: {reference} Given: {given}"


def assert_less_than(
    reference: Any, given: Any, message: str = "Value should be less than:"
) -> None:
    """Assert that the given value is less than the reference value."""
    assert (
        reference < given
    ), f"{message} Reference: {reference} Given: {given}"


def assert_less_than_or_equals(
    reference: Any,
    given: Any,
    message: str = "Value should be less or equal than:",
) -> None:
    """Assert that the given value is less than or equals the reference value."""
    assert (
        reference <= given
    ), f"{message} Reference: {reference} Given: {given}"


# Blacklist
BLACKLIST: List[str] = [
    r"__.*__",  # Python magic methods
    "quit",  # Quit the browser
    "close",  # Close the current window
]

ADD_ACTION: Dict[str, Any] = {
    "sleep": sleep,
    "assert_equals": assert_equals,
    "assert_not_equals": assert_not_equals,
    "assert_true": assert_true,
    "assert_false": assert_false,
    "assert_greater_than": assert_greater_than,
    "assert_greater_than_or_equals": assert_greater_than_or_equals,
    "assert_less_than": assert_less_than,
    "assert_less_than_or_equals": assert_less_than_or_equals,
}


def call_callable_with_args(
    call: Callable, args: Optional[Union[Dict, List, int, float, str]] = None
) -> Any:
    """Call a callable with the given arguments.

    Parameters:
    - callable: The callable to call.
    - args: The arguments to call the callable with.

    Returns:
    The result of the callable.
    """
    if isinstance(args, dict):
        return call(**args)
    elif isinstance(args, list):
        return call(*args)
    elif args is not None:
        return call(args)
    else:
        return call()


def get_arguments(args: Any, element: Any) -> Arguments:
    """Get the arguments of an action.

    Parameters:
    -----------
    - args: Any
        The arguments.
    - element: Any
        The element.

    Returns:
    The arguments.
    """
    # List of arguments
    result: Any = None
    # Native types
    if (
        isinstance(args, bool)
        or isinstance(args, str)
        or isinstance(args, int)
        or isinstance(args, float)
    ):
        result = args
    # Lists are treated as lists of arguments
    # elif isinstance(args, list):
    #     # TODO: recursive
    #     for arg in args:
    #         result.extend(get_arguments(arg, element))
    # Dict can be everything
    elif isinstance(args, dict):
        arg_type = ArgumentType(args.get("type", None))
        if arg_type in (
            ArgumentType.LIST,
        ):
            result = []
            for arg in args["value"]:
                result.append(get_arguments(arg, element))
        elif arg_type in (
            ArgumentType.BOOLEAN,
            ArgumentType.STRING,
            ArgumentType.INTEGER,
            ArgumentType.FLOAT,
            ArgumentType.DICTIONARY,
        ):
            result = args["value"]
        elif arg_type == ArgumentType.EVAL:
            result = eval(args["value"])  # pylint: disable=eval-used
        elif arg_type == ArgumentType.ACTION:
            action: SeleniumAction = args["value"]
            result = run_action(action, element)
        elif arg_type == ArgumentType.NATIVE:
            result = get_native_argument(args["value"])

    return result


def get_set_or_call_attribute(
    clazz: Any, attribute: str, args: Arguments
) -> Any:
    """Get, set or call an attribute of a class.

    Parameters:
    - clazz: The class to get, set or call the attribute of.
    - attribute: The attribute to get, set or call.
    - args: The arguments to call the attribute with.

    Returns:
    The result of the attribute.
    """
    attribute_of_clazz = getattr(clazz, attribute)
    if callable(attribute_of_clazz):
        return call_callable_with_args(attribute_of_clazz, args)
    else:
        # Get attribute
        if args is None:
            return getattr(clazz, attribute)
        # Set attribute
        else:
            if type(attribute_of_clazz) != type(args):  # pylint: disable=unidiomatic-typecheck
                raise ValueError(
                    f"Type of attribute {attribute} is {type(attribute_of_clazz)}, but type of arg is {type(args)}."
                )
            else:
                setattr(clazz, attribute, args)

    return clazz


def run_action(action: SeleniumAction, element: Any) -> Any:
    """Run an action.

    Parameters:
    - action: The action to run.
    - element: The element to run the action on.

    Returns:
    The result of the action.
    """
    # Log the action
    test_tool_logger.info(action.get("log", f'Action {action["action"]}'))
    # Action is an extra action that is not part of Selenium
    if action["action"] in ADD_ACTION:
        result = call_callable_with_args(
            ADD_ACTION[action["action"]],
            get_arguments(action.get("args", None), element),
        )
    # Handle native functions
    elif action["action"].startswith("selenium.webdriver"):
        result = call_callable_with_args(
            get_native_function(action["action"]),
            get_arguments(action.get("args", None), element),
        )
    # Check if the action is in the blacklist
    elif action["action"] in BLACKLIST:
        raise ValueError(f'Action {action["action"]} is not allowed.')
    # Check if the action is available
    elif action["action"] not in dir(element):
        raise ValueError(f'Action {action["action"]} is not available.')
    else:
        # Call the callable with the arguments
        result = get_set_or_call_attribute(
            element,
            action["action"],
            get_arguments(action.get("args", None), element),
        )

    # Get and run the following actions
    actions = action.get("actions", [])
    new_result = result
    for sub_action in actions:
        new_result = run_action(sub_action, result)

    return new_result

"""
This module contains the functions to get the arguments
"""
from enum import Enum
from logging import getLogger
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union, Tuple
import re

from test_tool import DotDict
from test_tool_selenium_plugin.native import Selenium, get_native_argument

__all__ = ["ArgumentType", "SeleniumAction", "get_arguments", "run_action"]

# Get the logger
test_tool_logger = getLogger("test-tool")

# Type definition for arguments
Arguments = Optional[List[Union[Dict[Any, Any],
                                List[Any], str, int, float, bool]]]

PATTERN_PATH = r"^(((\.?[a-zA-Z0-9\_]+(\[\d+\])*)(\.[a-zA-Z0-9\_]+(\[\d+\])*)*)|\.)$"


class Operator(Enum):
    """
    This class represents an operator.
    """

    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="


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
    CONTEXT = "context"
    ACTION = "action"


class SeleniumAction(TypedDict):
    """
    The structure of a Selenium action.
    """

    action: str
    args: Arguments
    actions: List["SeleniumAction"]
    log: str
    # Since 3.11
    # actions: NotRequired[List["SeleniumAction"]]
    # log: NotRequired[str]


def assert_fn(
    operator: str,
    expected: Any,
    given: Any,
) -> None:
    """
    Make an assertion with the given operator, expected and given values.

    Parameters:
    -----------
    operator: str
        The operator to use for the assertion.
    expected: Any
        The expected value.
    given: Any
        The given value.

    Raises:
    -------
    ValueError
        If the operator is not supported.
    """
    # Parse the operator
    operator_enum: Operator = Operator(operator)

    # Make the assertion
    if operator_enum == Operator.EQUAL:
        assert expected == given, f"Expected: {expected} != Given: {given}"
    elif operator_enum == Operator.NOT_EQUAL:
        assert expected != given, f"Expected: {expected} == Given: {given}"
    elif operator_enum == Operator.LESS_THAN:
        assert expected < given, f"Expected: {expected} >= Given: {given}"
    elif operator_enum == Operator.LESS_THAN_OR_EQUAL:
        assert expected <= given, f"Expected: {expected} > Given: {given}"
    elif operator_enum == Operator.GREATER_THAN:
        assert expected > given, f"Expected: {expected} <= Given: {given}"
    elif operator_enum == Operator.GREATER_THAN_OR_EQUAL:
        assert expected >= given, f"Expected: {expected} < Given: {given}"
    else:
        raise ValueError(f"Operator {operator} is not supported.")


# Blacklist
BLACKLIST: List[str] = [
    r"__.*__",  # Python magic methods
    "quit",  # Quit the browser
    "close",  # Close the current window
]

ARTIFICIAL_CONTEXT: DotDict = DotDict({
    "assert": assert_fn,
    "selenium": Selenium,
    "sleep": sleep
})


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


def get_arguments(args: Any, context: Any) -> Arguments:
    """Get the arguments of an action.

    Parameters:
    -----------
    - args: Any
        The arguments.
    - context: Any
        The context.

    Returns:
    --------
    Arguments
        The arguments.
    """
    # List of arguments
    result: Any = None
    # Native types
    if (
        isinstance(args, bool)
        or isinstance(args, int)
        or isinstance(args, float)
    ):
        result = args
    # Strings are treated as strings or native functions
    elif isinstance(args, str):
        if args.startswith("selenium.webdriver") or args.startswith("."):
            tmp_context, action = get_new_context_and_action(context, args)
            if action:
                result = get_set_or_call_attribute(tmp_context, action)
            else:
                result = tmp_context
        else:
            result = args
    # Lists are treated as lists of arguments
    elif isinstance(args, list):
        result = []
        for arg in args:
            result.append(get_arguments(arg, context))
    # Dict can be everything
    elif isinstance(args, dict):
        arg_type = ArgumentType(args.get("type", None))
        if arg_type in (
            ArgumentType.LIST,
        ):
            result = []
            for arg in args["value"]:
                result.append(get_arguments(arg, context))
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
            action: SeleniumAction = args["value"]  # type: ignore
            result = run_action(action, context)  # type: ignore
        elif arg_type == ArgumentType.CONTEXT:
            result = get_native_argument(args["value"])

    return result


def get_set_or_call_attribute(
    clazz: Any, attribute: str, args: Arguments = None
) -> Any:
    """Get, set or call an attribute of a class.

    Parameters:
    ----------
    - clazz: Any
        The class to get, set or call the attribute on.
    - attribute: str
        The attribute to get, set or call.
    - args: Arguments
        The arguments to call the attribute with.

    Returns:
    --------
    Any
        The result of the action.
    """
    attribute_of_clazz = getattr(clazz, attribute)
    # We call if it is a function
    if callable(attribute_of_clazz):
        return call_callable_with_args(attribute_of_clazz, args)
    else:
        # Get attribute
        if args is None:
            return getattr(clazz, attribute)
        # Set attribute
        else:
            # pylint: disable-next=unidiomatic-typecheck
            if type(attribute_of_clazz) != type(args):
                raise ValueError(
                    f"Type of attribute {attribute} is "
                    + f"{type(attribute_of_clazz)}, " +
                    f"but type of arg is {type(args)}."
                )
            else:
                setattr(clazz, attribute, args)

    return clazz


def get_new_context_and_action(context: Any, path: str) -> Tuple[Any, str]:
    """Get the new context of an action.

    Parameters:
    ----------
    - context: Any
        The context to get the new context from.
    - path: str
        The path to the new context.

    Returns:
    --------
    Tuple[Any, str]
        The new context and the action.
    """
    # Validate with regex
    if not re.match(PATTERN_PATH, path):
        raise ValueError(f"Path {path} is not valid.")

    # Split the action into parts
    path_parts = path.split(".")

    # Remove empty parts, except the first one
    path_parts = [part for idx,  part in enumerate(
        path_parts) if part or idx == 0]

    # Check if list is empty
    if not path_parts:
        raise ValueError(f"Path {path} is not valid.")

    # Navigate to the previous part
    if path_parts[0]:
        tmp_context = ARTIFICIAL_CONTEXT
    else:
        tmp_context = context
        if len(path_parts) > 1:
            path_parts = path_parts[1:]

    if len(path_parts) > 1:
        for path_part in path_parts[:-1]:
            tmp_context = getattr(tmp_context, path_part)

    return tmp_context, path_parts[-1]


def run_action(action: SeleniumAction, context: Any) -> Any:
    """Run an action with the given context.

    Parameters:
    ----------
    - action: SeleniumAction
        The action to run.
    - context: Any
        The context to run the action with.

    Returns:
    --------
    Any
        The result of the action.
    """
    # Log the action
    test_tool_logger.info(action.get("log", f'Run action {action["action"]}'))

    # Get the new context and the real action
    tmp_context, real_action = get_new_context_and_action(
        context, action["action"])

    # Get the arguments
    arguments = get_arguments(action.get("args", None), context)

    if real_action in BLACKLIST:
        raise ValueError(f'Action {action["action"]} is not allowed.')

    # Call the callable with the arguments
    result = get_set_or_call_attribute(
        tmp_context,
        real_action,
        arguments,
    )

    # Get and run the following actions, the context is the result of the current action
    follow_up_actions: List[SeleniumAction] = action.get("actions", [])
    new_result = result
    for follow_up_action in follow_up_actions:
        new_result = run_action(follow_up_action, result)

    # Return the result
    return new_result

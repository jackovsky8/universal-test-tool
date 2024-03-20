"""
Docstring for the main module.
"""
from enum import Enum
from importlib import import_module
from logging import info
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


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


def native_webriver_function(data: str) -> None:
    # import selenium.webdriver programmatically
    print("native_webriver_function")


# Blacklist
BLACKLIST: List[str] = [
    r"__.*__",  # Python magic methods
    "quit",  # Quit the browser
    "close",  # Close the current window
]

ADD_ACTION: Dict[str, Any] = {
    "sleep": sleep,
    "wait": WebDriverWait,
    "native_webriver_function": native_webriver_function,
    "assert_equals": assert_equals,
    "assert_not_equals": assert_not_equals,
    "assert_true": assert_true,
    "assert_false": assert_false,
    "assert_greater_than": assert_greater_than,
    "assert_greater_than_or_equals": assert_greater_than_or_equals,
    "assert_less_than": assert_less_than,
    "assert_less_than_or_equals": assert_less_than_or_equals,
}

# Type definition for arguments
Arguments = List[Union[Dict[Any, Any], List[Any], str, int, float, bool]]


class BrowserType(Enum):
    """
    Enum for the different browser types.
    """

    CHROME = "chrome"
    GECKO = "gecko"
    CHROMIUM_EDGE = "chromium-edge"


# Define the mapping between the browser type and the driver manager
BROWSER_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: ChromeDriverManager,
    BrowserType.GECKO: GeckoDriverManager,
    BrowserType.CHROMIUM_EDGE: EdgeChromiumDriverManager,
}

# Define the mapping between the browser type and the options
BROWSER_OPTIONS_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: ChromeOptions,
    BrowserType.GECKO: FirefoxOptions,
    BrowserType.CHROMIUM_EDGE: ChromiumOptions,
}

# Define the mapping between the browser type and the driver
BROWSER_DRIVER_MAPPING: Dict[BrowserType, Callable] = {
    BrowserType.CHROME: webdriver.Chrome,
    BrowserType.GECKO: webdriver.Firefox,
    BrowserType.CHROMIUM_EDGE: webdriver.ChromiumEdge,
}


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
    ACTION = "action"


class SeleniumCall(TypedDict):
    """
    The structure of a Selenium call.
    """

    actions: List["SeleniumAction"]
    base_url: str
    path: str
    url: Optional[str]
    webdriver: List[BrowserType]


class SeleniumAction(TypedDict):
    """
    The structure of a Selenium action.
    """

    action: str
    args: Optional[Arguments]
    actions: Optional[List["SeleniumAction"]]
    log: Optional[str]


# Define the default call
default_selenium_call: SeleniumCall = {
    "actions": [],
    "base_url": "{{GUI_BASE_URL}}",
    "path": "{{GUI_PATH}}",
    "url": None,
    "webdriver": ["chrome"],
}


def import_plugin(plugin: str) -> bool:
    # # Dynamically import the specified components from the module
    # try:
    #     plugin_module = import_module(
    #         PLUGIN_NAME_TEMPLATE.replace("${plugin}", plugin.lower()))
    # except ModuleNotFoundError as e:
    #     error(
    #         f"Plugin {plugin} not found, try to install it with pip install test_tool_{plugin.lower()}_plugin")
    #     return False

    # # Create a dict for the loaded plugin
    # loaded_plugin: Dict[str, Any] = dict()

    # # Load the components from the plugin
    # to_load = [el.replace("${plugin}", plugin.lower())
    #            for el in PLUGIN_TEMPLATE]
    # try:
    #     for component in to_load:
    #         key: str = component.replace(f"{plugin.lower()}_", "")
    #         loaded_plugin[key] = getattr(plugin_module, component)
    #         if type(loaded_plugin[key]) != PLUGIN_COMPONENT_TYPES[key]:
    #             error(
    #                 f"Module test_tool_{plugin.lower()}_plugin is not a valid plugin, {component} is not a {PLUGIN_COMPONENT_TYPES[key]}")
    #             return False
    # except AttributeError as e:
    #     error(
    #         f"Module test_tool_{plugin.lower()}_plugin is not a valid plugin, missing a component.")
    #     return False

    # LOADED_CALL_TYPES[plugin] = loaded_plugin
    return True


def make_selenium_call(call: SeleniumCall, data: Dict[str, Any]) -> None:
    """
    Make a Selenium call.

    Parameters:
    -----------
    call: SeleniumCall
        The call to make.
    data: Dict[str, Any]
        The data to make the call with.
    """
    info(f'Selenium Call wit url {call["url"]}')

    # For each webdriver
    for web_driver in call["webdriver"]:
        # Install the webdriver
        BROWSER_MAPPING[web_driver]().install()

        # Create browser options
        browser_options = BROWSER_OPTIONS_MAPPING[web_driver]()
        for option in call["options"].keys():
            if option in BLACKLIST:
                raise ValueError(f"Option {option} is not allowed.")
            elif option not in dir(browser_options):
                raise ValueError(f"Action {option} is not available.")
            else:
                get_set_or_call_attribute(
                    browser_options,
                    option,
                    get_arguments(call["options"][option], browser_options),
                )

        # Create a new instance of the Chrome driver
        driver = BROWSER_DRIVER_MAPPING[web_driver](options=browser_options)

        # Open the website
        driver.get(call["url"])

        # Run some actions on the website
        for action in call["actions"]:
            run_action(action, driver)

        # Quit the browser
        driver.quit()


def run_action(action: SeleniumAction, element: Any) -> Any:
    """Run an action.

    Parameters:
    - action: The action to run.
    - element: The element to run the action on.

    Returns:
    The result of the action.
    """
    # Log the action
    info(action.get("log", f'Action {action["action"]}'))
    # Action is an extra action that is not part of Selenium
    if action["action"] in ADD_ACTION.keys():
        result = call_callable_with_args(
            ADD_ACTION[action["action"]],
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


def get_arguments(args: Any, element: Any) -> Arguments:
    """Get the arguments of an action.

    Parameters:
    - args: The arguments to get.
    - element: The element to get the arguments for.

    Returns:
    The arguments.
    """
    # List of arguments
    result: Arguments = []
    # Native types
    if (
        isinstance(args, bool)
        or isinstance(args, str)
        or isinstance(args, int)
        or isinstance(args, float)
    ):
        result.append(args)
    # Dict can be everything
    elif isinstance(args, dict):
        arg_type = ArgumentType(args.get("type", None))
        if arg_type in (
            ArgumentType.BOOLEAN,
            ArgumentType.STRING,
            ArgumentType.INTEGER,
            ArgumentType.FLOAT,
            ArgumentType.LIST,
            ArgumentType.DICTIONARY,
        ):
            result.append(args["value"])
        elif arg_type == ArgumentType.EVAL:
            result.append(eval(args["value"]))
        elif arg_type == ArgumentType.ACTION:
            action: SeleniumAction = args["value"]
            result.append(run_action(action, element))
    # List can be a list of everything
    elif isinstance(args, list):
        for arg in args:
            result.extend(get_arguments(arg, element))

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
        if len(args) == 0:
            return getattr(clazz, attribute)
        # Set attribute
        else:
            if isinstance(attribute_of_clazz, bool):
                if not len(args) == 1 or not isinstance(args[0], bool):
                    raise ValueError(
                        f"Option {attribute} is a boolean, but arg isn't."
                    )
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, str):
                if not len(args) == 1 or not isinstance(args[0], str):
                    raise ValueError(
                        f"Option {attribute} is a string, but arg isn't."
                    )
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, int):
                if not len(args) == 1 or not isinstance(args[0], int):
                    raise ValueError(
                        f"Option {attribute} is an integer, but arg isn't."
                    )
                else:
                    setattr(clazz, attribute, args[0])
            elif isinstance(attribute_of_clazz, float):
                if not len(args) == 1 or not isinstance(args[0], float):
                    raise ValueError(
                        f"Option {attribute} is a float, but arg isn't."
                    )
                else:
                    setattr(clazz, attribute, args[0])
            else:
                # Setter no implemented for other values
                raise NotImplementedError(
                    f"Option {attribute} is of type {type(attribute_of_clazz)}."
                )

    return clazz


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


# Define the function that will be called before the function above


def augment_selenium_call(call: SeleniumCall, data: Dict, path: Path) -> None:
    """Augment the call.

    Parameters:
    - call: The call to augment.
    - data: The data to augment the call with.
    - path: The path of the call.

    Returns:
    Nothing.
    """
    # Augment the url
    if call["url"] is None:
        call["url"] = f'{call["base_url"]}{call["path"]}'

    # The webdriver is a list of browser types
    call["webdriver"] = [BrowserType(driver) for driver in call["webdriver"]]


# Define the main function
def main() -> None:
    """
    The main function.^
    """
    print("test-tool-selenium-plugin")

"""
This module contains the functions to run native webdriver functions.
"""
import inspect
from importlib import import_module
from importlib.util import find_spec
from logging import getLogger
from typing import Any, Callable, Dict, Optional

from test_tool import DotDict

__all__ = ["get_native_function", "get_native_argument"]

# Get the logger
test_tool_logger = getLogger("test-tool")

stored_native_functions = DotDict({})


class LazyLoadDict(object):
    """
    A wrapper class for the Selenium WebDriver native functions and arguments.
    """

    def __init__(self, path: str, parent: Optional["LazyLoadDict"] = None):
        self.__path__ = path
        self.__parent__ = parent
        self.__data__: Dict[str, Any] = {}

    def __hasattr__(self, name: str) -> bool:
        return hasattr(self, name)

    def __getattr__(self, name: str) -> Any:
        if self.__data__.get('name') is None:
            if module_exists(f"{self.__path__}.{name}"):
                self.__data__[name] = LazyLoadDict(
                    f"{self.__path__}.{name}", self)
            elif self.__parent__:
                return self.__parent__.__import_module__(f"{self.__path__}.{name}")
            else:
                raise ModuleNotFoundError(
                    f"module {self.__path__}.{name} not found")

        return self.__data__[name]

    def __import_module__(self, name: str) -> Any:
        names = name.removeprefix(f"{self.__path__}.").split(".")
        required_name = names[1]
        actual_module_name = names[0]

        module = import_module(f"{self.__path__}.{actual_module_name}")
        self.__data__[actual_module_name] = module
        return getattr(self.__data__[actual_module_name], required_name)


class Selenium(object):
    """
    A wrapper class for the Selenium WebDriver native functions and arguments.
    """

    webdriver: LazyLoadDict = LazyLoadDict('selenium.webdriver')


def module_exists(module: str) -> bool:
    """
    Check if a module exists.

    Parameters:
    -----------
    module: str
        The module to check.
    """
    try:
        find_spec(module)
        return True
    except ModuleNotFoundError:
        return False


def import_native(plugin: str, loaded_call_types: Dict) -> bool:
    """
    Import a function from a plugin.

    Parameters:
    -----------
    plugin: str
        The plugin to import the function from.
    loaded_call_types: Dict
        The loaded call types.
    """
    # Cut the function name from the plugin
    el_idx: int = -1
    el_str: str = plugin.split(".")[el_idx]
    plugin_str: str = ".".join(plugin.split(".")[0:el_idx])

    # Check if the plugin is already loaded
    actual: Dict[str, Dict] = loaded_call_types
    key_history = []
    for key in plugin_str.split("."):
        key_history.append((actual, key))
        if key in actual and (isinstance(actual[key], DotDict) or inspect.isclass(actual[key])):
            actual = actual[key]
        else:
            actual[key] = DotDict({})
            actual = actual[key]
    if inspect.isclass(actual):
        return hasattr(actual, el_str)
    elif el_str in actual:
        return True

    # Dynamically import the specified components from the module
    done: bool = False
    while not done:
        try:
            plugin_module = import_module(plugin_str)
            done = True
        except ModuleNotFoundError as e:
            last_key = key_history.pop()
            del last_key[0][last_key[1]]
            actual = last_key[0]
            el_idx -= 1
            el_str = plugin.split(".")[el_idx]
            plugin_str = ".".join(plugin.split(".")[0:el_idx])
            if not plugin_str:
                raise ModuleNotFoundError(
                    f"No module named '{plugin}'") from e

    # Load the function from the plugin
    test_tool_logger.debug(
        "Loading function %s from plugin %s", el_str, plugin)
    try:
        actual[el_str] = getattr(plugin_module, el_str)
    except ModuleNotFoundError as e:
        test_tool_logger.debug("Function %s not found in plugin %s",
                               el_str, plugin)
        raise e

    return True


def get_native_function(name: str) -> Callable:
    """
    Call a native Selenium WebDriver function.

    Parameters:
    -----------
    data: str
        The data to call the function with.
    """
    if not name.startswith("selenium.webdriver."):
        raise ValueError("Function is not a native function")

    import_native(name, stored_native_functions)

    # Get the argument
    keys = name.split(".")
    actual = stored_native_functions
    for key in keys:
        if isinstance(actual, DotDict):
            actual = actual[key]
        else:
            actual = getattr(actual, key)

    if not callable(actual):
        raise ValueError("Function is not callable")
    else:
        return actual


def get_native_argument(name: str) -> Any:
    """
    Get a native argument.

    Parameters:
    -----------
    name: str
        The name of the argument to get.
    """

    if not name.startswith("selenium.webdriver."):
        raise ValueError("Argument is not a native argument")

    import_native(name, stored_native_functions)

    # Get the argument
    keys = name.split(".")
    actual = stored_native_functions
    for key in keys:
        if isinstance(actual, DotDict):
            actual = actual[key]
        else:
            actual = getattr(actual, key)

    return actual

"""
In this file, we import the necessary modules for the test tool to run.
"""
from importlib import import_module
from logging import getLogger
from types import FunctionType
from typing import Any, Callable, Dict, TypedDict
from copy import deepcopy

# Get the logger
test_tool_logger = getLogger("test-tool")


class CallType(TypedDict):
    """
    Call Type.
    """

    default_call: Dict[str, Any]
    augment_call: Callable
    make_call: Callable


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

PLUGIN_DEFAULT: CallType = {
    "default_call": {},
    "augment_call": lambda *args, **kwargs: None,
    "make_call": lambda *args, **kwargs: None,
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
    loaded_plugin: CallType = deepcopy(PLUGIN_DEFAULT)

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

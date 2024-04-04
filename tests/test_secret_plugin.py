"""
This module contains tests for the selenium plugin.
"""
from copy import deepcopy
import test_tool_secret_plugin.main as test_tool_secret_plugin

# https://Sgithub.com/ClinicalGraphics/keyring-pybridge

# python on windows, pip install keyring, https://superuser.com/questions/49104/how-do-i-find-the-location-of-an-executable-in-windows


def test_make_secret_call() -> None:
    """
    Test the make_secret_call function.
    """

    call = deepcopy(test_tool_secret_plugin.default_secret_call)
    call["env"] = [
        {
            "name": "PYTHON_KEYRING_BACKEND",
            "value": "keyring_pybridge.PyBridgeKeyring",
        },
        {
            "name": "KEYRING_PROPERTY_PYTHON",
            "value": "/mnt/c/Users/graf/.keyring-pybridge/Scripts/python.exe",
        },
    ]

    test_tool_secret_plugin.get_secret = lambda prompt: "password"
    password = test_tool_secret_plugin.make_secret_call(call)

    assert password == "password"

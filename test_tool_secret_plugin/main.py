"""
Module for the secret plugin."""
import os
from getpass import getpass
from logging import getLogger
from typing import TypedDict

from keyring import delete_password, get_password, set_password
from keyring.errors import KeyringError

# Get the logger
test_tool_logger = getLogger("test-tool")


class Environment(TypedDict):
    """
    This class represents an environment.
    """

    name: str
    value: str


class SecretCall(TypedDict):
    """
    This class represents an secret call.
    """

    servicename: str
    username: str
    password: str
    env: list[Environment]


# Define the default call
default_secret_call: SecretCall = {
    "servicename": "test-tool-secret-plugin",
    "username": "username",
    "password": "password",
    "env": [],
}


def get_secret(prompt: str) -> str:
    """
    This function will be called to get the secret.

    Parameters:
    ----------
    prompt: str
        The prompt to enter the secret

    Returns:
    -------
    str
        The secret
    """
    return getpass(prompt)


def delete_secret(servicename: str, username: str) -> None:
    """
    This function will be called to delete the secret.

    Parameters:
    ----------
    servicename: str
        The servicename
    username: str
        The username
    """
    try:
        delete_password(servicename, username)
        test_tool_logger.debug("Deleted password from keyring")
    except KeyringError:
        pass


def make_secret_call(call: SecretCall) -> str:
    """
    This function will be called to make the secret call.

    Parameters:
    ----------
    call: SecretCall
        The call to make
    data: Dict
        The data that was passed to the function
    """

    for env in call["env"]:
        os.environ[env["name"]] = env["value"]

    try:
        password = get_password(call["servicename"], call["username"])
    except KeyringError:
        pass

    if not password:
        test_tool_logger.debug("Password not found in keyring")
        password = get_secret(
            f"Enter password for service '{call['servicename']}' and user '{call['username']}': "
        )
        try:
            set_password(call["servicename"], call["username"], password)
            test_tool_logger.debug("Password saved in keyring")
        except KeyringError:
            pass

    return password


def main() -> None:
    """
    This function will be called when the plugin is loaded.
    """
    print("test-tool-secret-plugin")

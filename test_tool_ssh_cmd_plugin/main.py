"""
This is a plugin for the universal test tool.

It provides the ability to run commands on a remote host via SSH.
"""
from logging import error, info
from pathlib import Path
from typing import Any, Callable, Dict, TypedDict

from paramiko import AutoAddPolicy, SSHClient


class SshCmdCall(TypedDict):
    """
    Class for SshCmdCall.
    """

    user: str
    password: str
    host: str
    cmd: str
    return_code: int


default_ssh_cmd_call: SshCmdCall = {
    "user": "{{REMOTE_CMD_USER}}",
    "password": "{{REMOTE_CMD_PASSWORD}}",
    "host": "{{REMOTE_CMD_HOST}}",
    "cmd": "",
    "return_code": 0,
}


def run_with_ssh_client(
    user: str, host: str, password: str, call: Callable[[SSHClient], None]
) -> None:
    """
    Run the callable with an SSH client.

    Parameters
    ----------
    user : str
        The user name.
    host : str
        The host name.
    password : str
        The password.
    call : Callable[[SSHClient], None]
        The callable.
    """
    # Create an SSH client
    info(f"Connect to {user}@{host}")
    client = SSHClient()

    # Automatically add the server's host key
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        # Connect to the remote server
        client.connect(host, username=user, password=password)

        # Run the callable
        call(client)
    finally:
        # Close the SSH connection
        client.close()


def run_ssh_cmd(
    client: SSHClient, cmd: str, expected_return_code: int
) -> None:
    """
    Run an SSH command.

    Parameters
    ----------
    client : SSHClient
        The SSH client.
    cmd : str
        The command.
    expected_return_code : int
        The expected return code.
    """
    # Execute the command
    _, stdout, stderr = client.exec_command(cmd)

    # Read and print the output
    output_str = stdout.read().decode("utf-8")
    error_str = stderr.read().decode("utf-8")
    if output_str:
        info(output_str.strip().strip("'").strip('"'))
    if error_str:
        error(error_str.strip().strip("'").strip('"'))

    # Check the return code
    return_code = stdout.channel.recv_exit_status()
    if expected_return_code is not None:
        equals: bool = return_code == expected_return_code
        assert (
            equals
        ), f"Expected return code {expected_return_code}, got {return_code}"
    else:
        info(f"SSH Command return with code: {return_code}")


def make_ssh_cmd_call(call: SshCmdCall, data: Dict[str, Any]) -> None:
    """
    Make an SSH command call.

    Parameters
    ----------
    call : SshCmdCall
        The call.
    data : Dict[str, Any]
        The data.
    """
    info(f'Run the cmd {call["cmd"]} remotely.')
    # Run the cmd with client
    run_with_ssh_client(
        call["user"],
        call["host"],
        call["password"],
        lambda client: run_ssh_cmd(client, call["cmd"], call["return_code"]),
    )


def augment_ssh_cmd_call(call: SshCmdCall, data: Dict, path: Path) -> None:
    """
    Augment an SSH command call.

    Parameters
    ----------
    call : SshCmdCall
        The call.
    data : Dict
        The data.
    path : Path
        The path.
    """
    if call["return_code"] is not None:
        call["return_code"] = int(call["return_code"])


def main() -> None:
    """
    Main function.
    """
    print("test-tool-ssh-cmd-plugin")

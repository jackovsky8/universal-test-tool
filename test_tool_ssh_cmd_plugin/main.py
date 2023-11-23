from logging import debug, error, info
from pathlib import Path
from typing import Any, Callable, Dict, List

from paramiko import AutoAddPolicy, SSHClient


class SshCmdCall():
    user: str
    password: str
    host: str
    cmd: List[str]

default_ssh_cmd_call: SshCmdCall = {
    'user': '${REMOTE_CMD_USER}',
    'password': '${REMOTE_CMD_PASSWORD}',
    'host': '${REMOTE_CMD_HOST}',
    'cmd': None
}

def run_with_ssh_client(user: str, host: str, password: str, callable: Callable[[SSHClient], None]) -> None:
    # Create an SSH client
    info(f'Connect to {user}@{host}')
    client = SSHClient()

    # Automatically add the server's host key
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        # Connect to the remote server
        client.connect(host, username=user, password=password)

        # Run the callable
        callable(client)
    finally:
        # Close the SSH connection
        client.close()

def run_ssh_cmd(client: SSHClient, cmd: str) -> None:
    # Execute the command
    stdin, stdout, stderr = client.exec_command(cmd)

    # Read the output
    output_str = stdout.read().decode("utf-8")
    error_str = stderr.read().decode("utf-8")

    # Check the return code
    return_code = stdout.channel.recv_exit_status()
                        
    # Check if the command was successful
    if return_code != 0:
        error(f"Error: Command failed with return code {return_code}")
    else:
        info(f"Success: Command succeeded with return code {return_code}")
                
    if output_str:
        info(output_str.strip().strip("'").strip('"'))
    if error_str:
        error(error_str.strip().strip("'").strip('"'))
                    
    # TODO we could check other return codes as well
    assert return_code == 0

def make_ssh_cmd_call(call: SshCmdCall, data: Dict[str, Any]) -> None:
    info(f'Run the cmd {call["cmd"]} remotely.')
    # Run the cmd with client
    run_with_ssh_client(call['user'], call['host'], call['password'], lambda client: run_ssh_cmd(client, call['cmd']))

def augment_ssh_cmd_call(call: SshCmdCall, data: Dict, path: Path) -> None:
    pass

def main() -> None:
    print('test-tool-ssh-cmd-plugin')
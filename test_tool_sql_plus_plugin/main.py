"""
Module for the sql plus plugin.
"""
from logging import debug, error, info
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Event, Thread
from typing import Any, Dict, List, TypedDict


class SqlPlusNotAvailable(Exception):
    """
    This class represents an exception if the sql plus
    command is not available.
    """


class SqlPlusCall(TypedDict):
    """
    This class represents a sql plus call.
    """

    file: Path
    command: str
    connection: str
    username: str
    password: str


default_sql_plus_call: SqlPlusCall = {
    "file": None,  # type: ignore
    "command": "sqlplus",
    "connection": "{{DB_CONNECTION}}",
    "username": "{{DB_USERNAME}}",
    "password": "{{DB_PASSWORD}}",
}


def log_output(
    pipe,
    prefix: str,
    output_list: List,
    is_error: bool,
    stop_event: Event,
) -> None:
    """
    This function logs the output of the pipe.

    Parameters
    ----------
    pipe : Any
        The pipe to log.
    prefix : str
        The prefix to use.
    output_list : List
        The list to store the output in.
    is_error : bool
        True if the pipe is an error pipe, False otherwise.
    stop_event : Event
        The stop event.
    """
    if is_error:
        log = error
    else:
        log = info

    for line in iter(pipe.readline, b""):
        if line.strip():
            log(f"{prefix}: {line.strip()}")
            output_list.append(line)
        # Stop the thread if the stop event is set
        if stop_event and stop_event.is_set():
            break


def run_cmd(command: str) -> str:
    """
    This function runs the command.

    Parameters
    ----------
    command : str
        The command to run.

    Returns
    -------
    str
        The output of the command.

    Raises
    ------
    AssertionError
        If the return code is not 0.
    """
    process = Popen(
        command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True
    )
    debug(f"Run command: {command}")

    # Create an event to signal threads to stop
    stop_event = Event()

    # Start threads to read output and error streams
    output_list: List[str] = []
    output_thread = Thread(
        target=log_output,
        args=(process.stdout, "Output", output_list, False, stop_event),
    )
    error_thread = Thread(
        target=log_output,
        args=(process.stderr, "Error", output_list, True, stop_event),
    )

    output_thread.start()
    error_thread.start()

    return_code = process.wait()
    assert (
        return_code == 0
    ), f"Sqlplus command failed with return code {return_code}"

    # Signal the threads to stop
    stop_event.set()

    # Wait for the threads to finish
    output_thread.join()
    error_thread.join()

    return "".join(output_list).strip()


def check_sql_plus(command: str) -> None:
    """
    This function checks if the sql plus command is available.

    Parameters
    ----------
    command : str
        The sql plus command to check.

    Raises
    ------
    SqlPlusNotAvailable
        If the sql plus command is not available.
    """
    command = f"{command} -v"
    try:
        result = run_cmd(command)
        if result.startswith("SQL*Plus:"):
            return
    except AssertionError:
        pass

    raise SqlPlusNotAvailable("Sql plus command not available.")


def run_sql(
    command: str, file: Path, connection: str, username: str, password: str
) -> None:
    """
    This function runs the sql plus command.
    """
    command = f'echo quit | {command} -S {username}/{password}@"{connection}" @{file}'
    run_cmd(command)


def make_sql_plus_call(call: SqlPlusCall, data: Dict[str, Any]) -> None:
    """
    This function makes the sql plus call.

    Parameters
    ----------
    call : SqlPlusCall
        The sql plus call to make.
    data : Dict[str, Any]
        The data dictionary.
    path : Path
        The path to the test file.
    """
    info(f'Run sql file: {call["file"]}')

    # Check if the sql plus command is available
    check_sql_plus(call["command"])

    # Run the sql plus command
    run_sql(
        call["command"],
        call["file"],
        call["connection"],
        call["username"],
        call["password"],
    )


def augment_sql_plus_call(
    call: SqlPlusCall, data: Dict[str, Any], path: Path
) -> None:
    """
    This function augments the sql plus call with the default values.

    Parameters
    ----------
    call : SqlPlusCall
        The sql plus call to augment.
    data : Dict[str, Any]
        The data dictionary.
    path : Path
        The path to the test file.
    """
    if call["file"] is None:
        raise ValueError("The file parameter is required.")
    else:
        call["file"] = path.joinpath(call["file"])


def main() -> None:
    """
    This is the main entry point of the plugin.
    """
    print("test-tool-sql-plus-plugin")

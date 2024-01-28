"""
Module for the test-tool-run-process-plugin.
"""
from enum import Enum
from errno import ESRCH
from io import TextIOWrapper
from json import loads
from logging import DEBUG, debug, error, info, root
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Event, Thread, Timer
from typing import Any, Dict, Hashable, List, Optional, TypedDict


class RunProcessSaveType(Enum):
    """
    This class represents the type of the save.
    """

    JSON = 1
    STRING = 2


class BashProgramType(Enum):
    """
    This class represents the type of the bash program.
    """

    BASH = "/bin/bash"
    SH = "/bin/sh"
    ZSH = "/bin/zsh"
    POWERSHELL = "powershell.exe"
    CMD = "cmd.exe"


class RunProcessSave(TypedDict):
    """
    This class represents a run process save.
    """

    name: str
    type: RunProcessSaveType
    path: Optional[List[str]]


class RunProcessCall(TypedDict):
    """
    This class represents a run process call.
    """

    cmd: str
    timeout: int
    save: Optional[RunProcessSave]
    shell: bool
    text: bool
    program: BashProgramType
    return_code: Optional[int]


append_to_run_process_call: Dict[Hashable, str] = {
    BashProgramType.BASH: "\nexit\n",
    BashProgramType.SH: "\nexit\n",
    BashProgramType.ZSH: "\nexit\n",
    BashProgramType.POWERSHELL: "\nExit\n",
    BashProgramType.CMD: "\nExit\n",
}

default_run_process_call: RunProcessCall = {
    "cmd": None,  # type: ignore
    "timeout": 0,
    "save": None,
    "shell": True,
    "text": True,
    "program": "/bin/bash",  # type: ignore
    "return_code": 0,
}


def log_output(
    pipe,
    prefix: str,
    is_error: bool,
    output_list: List,
    stop_event: Event,
):
    """
    Log the output of a pipe.

    Parameters
    ----------
    pipe : IO
        The pipe.
    prefix : str
        The prefix.
    is_error : bool
        If the pipe is an error pipe.
    output_list : List
        The output list.
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


def timeout_cmd(p: Popen):
    """
    Timeout a cmd.

    Parameters
    ----------
    p : Popen
        The cmd.
    """
    if p.poll() is None:
        try:
            p.terminate()
            if DEBUG >= root.level:
                error("Timeout for cmd reached.")
            exit(1)
        except OSError as e:
            if e.errno != ESRCH:
                raise


def run_cmd(
    command: str,
    timeout: float,
    shell: bool,
    text: bool,
    program: BashProgramType,
    expected_return_code: Optional[int],
) -> str:
    """
    Run a cmd.

    Parameters
    ----------
    command : str
        The command.
    timeout : float
        The timeout.
    shell : bool
        If the command should be run in a shell.
    text : bool
        If the command should be run in text mode.
    program : BashProgramType
        The program.
    expected_return_code : Optional[int]
        The expected return code.

    Returns
    -------
    str
        The output of the cmd.
    """
    process = Popen(
        program.value,
        shell=shell,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE,
        text=text,
    )

    if timeout:
        # Start a timer that will kill the cmd if it runs too long
        t = Timer(interval=timeout, function=timeout_cmd, args=[process])
        t.start()

    # Create an event to signal threads to stop
    stop_event = Event()
    # Start threads to read output and error streams
    output_list: List[str] = []
    output_thread = Thread(
        target=log_output,
        args=(process.stdout, "Output", False, output_list, stop_event),
    )
    error_thread = Thread(
        target=log_output,
        args=(process.stderr, "Error", True, output_list, stop_event),
    )

    output_thread.start()
    error_thread.start()

    # Stream the output of the cmd but also store it in a list
    assert isinstance(process.stdin, TextIOWrapper)
    process.stdin.write(command + append_to_run_process_call[program])
    process.stdin.flush()

    return_code = process.wait()

    # Signal the threads to stop
    stop_event.set()
    # Wait for the threads to finish
    output_thread.join()
    error_thread.join()

    if timeout:
        t.cancel()

    if (
        expected_return_code is not None
        and return_code != expected_return_code
    ):
        error(
            f"Cmd terminated with code {return_code} insted of"
            + " {expected_return_code}."
        )
        assert False

    return "".join(output_list).strip()


def make_run_process_call(call: RunProcessCall, data: Dict[str, Any]) -> None:
    """
    Make a run process call.

    Parameters
    ----------
    call : RunProcessCall
        The call.
    data : Dict[str, Any]
        The data.
    """
    info(f'Run the cmd {call["cmd"]}.')

    result = run_cmd(
        call["cmd"],
        call["timeout"],
        call["shell"],
        call["text"],
        call["program"],
        call["return_code"],
    )

    if call["save"] is not None:
        if call["save"]["type"] is None:
            call["save"]["type"] = RunProcessSaveType.STRING
        else:
            try:
                call["save"]["type"] = RunProcessSaveType[
                    call["save"]["type"]
                ]  # type: ignore
            except KeyError as e:
                raise ValueError(
                    f"Save type {str(e)} is not supported."
                ) from e

        if call["save"]["type"] == RunProcessSaveType.JSON:
            val = loads(result.replace("'", '"'))
            try:
                call["save"]["path"]
            except KeyError:
                call["save"]["path"] = []

            for p in call["save"]["path"]:  # type: ignore
                val = val[p]

            debug(f'Save {val} as {call["save"]["name"]}')
            data[call["save"]["name"]] = val
        elif call["save"]["type"] == RunProcessSaveType.STRING:
            debug(f'Save {result} as {call["save"]["name"]}')
            data[call["save"]["name"]] = result


def augment_run_process_call(
    call: RunProcessCall,
    data: Dict[str, Any],  # pylint: disable=unused-argument
    path: Path,  # pylint: disable=unused-argument
) -> None:
    """
    Augment an run process call.

    Parameters
    ----------
    call : RunProcessCall
        The call.
    data : Dict
        The data.
    path : Path
        The path.
    """
    # timeout as int
    call["timeout"] = int(call["timeout"])

    # return_code as int
    if call["return_code"] is not None:
        call["return_code"] = int(call["return_code"])

    # Default save type is string
    if call["save"] is not None:
        if call["save"]["type"] is None:
            call["save"]["type"] = RunProcessSaveType.STRING

    try:
        call["program"] = BashProgramType(call["program"])
    except ValueError as e:
        raise ValueError(
            f'Program type {call["program"]} is not supported.'
        ) from e


def main() -> None:
    """
    Main function for the test-tool-run-process-plugin.
    """
    print("test-tool-run-process-plugin")

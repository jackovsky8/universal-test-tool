from enum import Enum
from errno import ESRCH
from json import loads
from logging import DEBUG, debug, error, info, root
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread, Timer, Event
from typing import Any, Dict, TypedDict, Hashable, List


class RunProcessSaveType(Enum):
    JSON = 1
    STRING = 2

class BashProgramType(Enum):
    BASH = '/bin/bash'
    SH = '/bin/sh'
    ZSH = '/bin/zsh'

class RunProcessSave(TypedDict):
    name: str
    type: str

class RunProcessCall():
    cmd: str
    timeout: int
    save: RunProcessSave
    shell: bool
    text: bool
    program: str
    return_code: int

append_to_run_process_call: Dict[Hashable, str] = {
    BashProgramType.BASH: '\nexit\n',
    BashProgramType.SH: '\nexit\n',
    BashProgramType.ZSH: '\nexit\n'
}

default_run_process_call: RunProcessCall = {
    'cmd': None,
    'timeout': None,
    'save': None,
    'shell': True,
    'text': True,
    'program': '/bin/bash',
    'return_code': None
}

def log_output(pipe, prefix: str, is_error: bool = False, output_list: List = [], stop_event: Event = None):
    if is_error:
        log = error
    else:
        log = info

    for line in iter(pipe.readline, b''):
        if line.strip():
            log(f'{prefix}: {line.strip()}')
            output_list.append(line)
        # Stop the thread if the stop event is set
        if stop_event and stop_event.is_set():
            break
        
def timeout_cmd(p: Popen):
    if p.poll() is None:
        try:
            p.terminate()
            if DEBUG >= root.level:
                error('Timeout for cmd reached.')
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
        expected_return_code: int) -> str:
    process = Popen(program.value, 
                        shell=shell,
                        stdout=PIPE,
                        stderr=PIPE,
                        stdin=PIPE,
                        text=text)
    
    if timeout:
        # Start a timer that will kill the cmd if it runs too long
        t = Timer(interval=timeout, function=timeout_cmd, args=[process])
        t.start()
            
    # Create an event to signal threads to stop
    stop_event = Event()
    # Start threads to read output and error streams
    output_list = []
    output_thread = Thread(target=log_output, args=(process.stdout, "Output", False, output_list, stop_event))
    error_thread = Thread(target=log_output, args=(process.stderr, "Error", True, output_list, stop_event))

    output_thread.start()
    error_thread.start()

    # Stream the output of the cmd but also store it in a list
    process.stdin.write(command + append_to_run_process_call[program])
    process.stdin.flush()

    return_code = process.wait()

    # Signal the threads to stop
    stop_event.set()
    # Wait for the threads to finish
    output_thread.join()
    error_thread.join()
    
    if timeout is not None:
        t.cancel()

    if expected_return_code is not None and return_code != expected_return_code:
        error(f'Cmd terminated with code {return_code} insted of {expected_return_code}.')
        assert False
    
    return ''.join(output_list).strip()

def make_run_process_call(call: RunProcessCall, data: Dict[str, Any]) -> None:
    info(f'Run the cmd {call["cmd"]}.')
    
    result = run_cmd(call['cmd'], call['timeout'], call['shell'], call['text'], call['program'], call['return_code'])

    if call['save'] is not None:
        try:
            call['save']['type'] = RunProcessSaveType[call['save']['type']]
        except KeyError as e:
            if "'type'" == str(e):
                call['type'] = RunProcessSaveType.STRING
            else:
                error(f'Save type {str(e)} is not supported.')

        if call['save']['type'] == RunProcessSaveType.JSON:
            val = loads(result.replace("'", '"'))
            for p in call['save']['path']:
                val = val[p]
            debug(f'Save {val} as {call["save"]["name"]}')
            data[call['save']['name']] = val
        elif call['save']['type'] == RunProcessSaveType.STRING:
            debug(f'Save {result} as {call["save"]["name"]}')
            data[call['save']['name']] = result

def augment_run_process_call(call: RunProcessCall, data: Dict, path: Path) -> None:
    # timeout as int
    if call['timeout'] is not None:
        call['timeout'] = int(call['timeout'])

    # return_code as int
    if call['return_code'] is not None:
        call['return_code'] = int(call['return_code'])

    # Default save type is string
    if call['save'] is not None:
        if call['save']['type'] is None:
            call['save']['type'] = RunProcessSaveType.STRING

    try:
        call['program'] = BashProgramType(call['program'])
    except ValueError as e:
        error(f'Program type {call["program"]} is not supported.')

def main() -> None:
    print('test-tool-bash-cmd-plugin')
from enum import Enum
from errno import ESRCH
from json import loads
from logging import DEBUG, debug, error, info, root
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Timer
from typing import Any, Dict, List, TypedDict


class LocalCmdSaveType(Enum):
    JSON = 1
    STRING = 2

class LocalCmdSave(TypedDict):
    name: str
    type: str

class LocalCmdCall():
    cmd: List[str]
    timeout: float
    save: LocalCmdSave

default_local_cmd_call: LocalCmdCall = {
    'cmd': None,
    'timeout': None,
    'save': None
}

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

def run_cmd(command: List[str], timeout: float = None) -> str:
    cmd = Popen(command, 
                        shell=False,
                        stdout=PIPE,
                        stderr=PIPE)
    
    if timeout is not None:
        # Wait 10 seconds for the login to finish, otw. kill the command
        t = Timer(interval=timeout, function=timeout_cmd, args=[cmd])
        t.start()
            
    info("Waiting for the cmd to finish...")
    return_code = cmd.wait()
    
    if timeout is not None:
        t.cancel()

    output = cmd.stdout.read()
    if output:
        info("Output:")
        info(output.decode().strip().strip("'").strip('"'))
    
    error_output = cmd.stderr.read()
    if error_output:
        error("Error output:")
        error(error_output.decode().strip().strip("'").strip('"'))

    if return_code != 0:
        error(f'Cmd terminated with code {return_code}.')
        assert False
    
    return output.decode().strip().strip("'").strip('"')

def make_local_cmd_call(call: LocalCmdCall, data: Dict[str, Any]) -> None:
    info(f'Run the cmd {" ".join(call["cmd"])}.')
    
    result = run_cmd(call['cmd'])

    if call['save'] is not None:
        try:
            call['save']['type'] = LocalCmdSaveType[call['save']['type']]
        except KeyError as e:
            if "'type'" == str(e):
                call['type'] = LocalCmdSaveType.STRING
            else:
                error(f'Save type {str(e)} is not supported.')

        if call['save']['type'] == LocalCmdSaveType.JSON:
            val = loads(result.replace("'", '"'))
            for p in call['save']['path']:
                val = val[p]
            debug(f'Save {val} as {call["save"]["name"]}')
            data[call['save']['name']] = val
        elif call['save']['type'] == LocalCmdSaveType.STRING:
            debug(f'Save {result} as {call["save"]["name"]}')
            data[call['save']['name']] = result

def augment_local_cmd_call(call: LocalCmdCall, data: Dict, path: Path) -> None:
    call['cmd'] = call["cmd"].split(' ')
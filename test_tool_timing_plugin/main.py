"""
This is a plugin for the universal test tool.

It provides the ability to run commands on a remote host via SSH.
"""
import time
import datetime
from enum import Enum
from logging import info
from pathlib import Path
from typing import Any, Dict, TypedDict


class Action(Enum):
    """
    Class for Action.
    """

    START = "start"
    STOP = "stop"


class TimingCall(TypedDict):
    """
    Class for TimingCall.
    """

    name: str
    action: Action


class TimingPluginData(TypedDict):
    """
    Class for TimingPluginData.
    """

    start_time: float
    stop_time: float
    duration: float


default_timing_call: TimingCall = {
    "name": "TIMER",
    "action": "start",  # type: ignore
}


def make_timing_call(call: TimingCall, data: Dict[str, Any]) -> None:
    """
    Make an SSH command call.

    Parameters
    ----------
    call : TimingCall
        The call.
    data : Dict[str, Any]
        The data.
    """
    t_data: TimingPluginData = data["timing_plugin_calls"][call["name"]]
    if call["action"] == Action.START:
        info(f'Start timer {call["name"]}')
        t_data["start_time"] = int(time.time() * 1e9)
        t_data["stop_time"] = t_data["start_time"]
        t_data["duration"] = 0.0
    elif call["action"] == Action.STOP:
        info(f'Stop timer {call["name"]}')
        t_data["stop_time"] = int(time.time() * 1e9)
        t_data["duration"] = t_data["stop_time"] - t_data["start_time"]

        data[f'TIMING_{call["name"]}_START_NANO'] = t_data["start_time"]
        data[f'TIMING_{call["name"]}_STOP_NANO'] = t_data["stop_time"]
        data[f'TIMING_{call["name"]}_DURATION_NANO'] = t_data["duration"]

        data[f'TIMING_{call["name"]}_START'] = datetime.datetime.utcfromtimestamp(
            t_data["start_time"] / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f UTC")
        data[f'TIMING_{call["name"]}_STOP'] = datetime.datetime.utcfromtimestamp(
            t_data["stop_time"] / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f UTC")
        data[f'TIMING_{call["name"]}_DURATION'] = datetime.datetime.utcfromtimestamp(
            t_data["duration"] / 1e9).strftime("%H:%M:%S.%f")


def augment_timing_call(call: TimingCall, data: Dict, path: Path) -> None:  # pylint: disable=unused-argument
    """
    Augment an Timing command call.

    Parameters
    ----------
    call : TimingCall
        The call.
    data : Dict
        The data.
    path : Path
        The path.
    """
    if "name" not in call:
        raise ValueError("The name is missing in the call.")
    else:
        call["name"] = str(call["name"]).upper()

    if "action" not in call:
        raise ValueError("The action is missing in the call.")
    else:
        call["action"] = Action(call["action"])  # type: ignore

    if "timing_plugin_calls" not in data:
        data["timing_plugin_calls"] = {}
    
    if call["name"] not in data["timing_plugin_calls"]:
        data["timing_plugin_calls"][call["name"]] = {
            "start_time": 0.0,
            "stop_time": 0.0,
            "duration": 0.0,
        }


def main() -> None:
    """
    Main function.
    """
    print("test-tool-timing-plugin")

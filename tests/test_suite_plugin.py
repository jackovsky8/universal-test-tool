"""
This module contains tests for the selenium plugin.
"""
import sys
from tempfile import gettempdir
from copy import deepcopy
from pathlib import Path
from shutil import rmtree
from typing import Dict

import pytest
from test_tool_suite_plugin import default_suite_call, make_suite_call
from yaml import dump

called: Dict[str, bool] = {}


@pytest.fixture(scope="function", autouse=True)
def create_test_mock() -> None:
    """
    Create a mock for the test tool plugin.
    """

    class Mock(object):
        """
        A mock class for test plugin.
        """

        @staticmethod
        def make_mock_call(
            call: Dict[str, str]
        ) -> None:  # pylint: disable=unused-argument
            """
            A mock function for make_timing_call.
            """
            called[call["name"]] = True

    sys.modules["test_tool_mock_plugin"] = Mock  # type: ignore


def test_make_suite_call() -> None:
    """
    Test the make_suite_call function.
    """

    call = deepcopy(default_suite_call)

    temporary_directory = Path(gettempdir()).joinpath(
        "test_tool/config"
    )
    # remove the folder if it exists
    rmtree(temporary_directory, ignore_errors=True)
    # create the folder
    temporary_directory.mkdir(exist_ok=True)

    # create the config
    test_data = {
        "data": "DATA",
    }
    # write as yaml
    with open(
        temporary_directory.joinpath("data.yaml"), "w", encoding="UTF-8"
    ) as file:
        file.write(dump(test_data))

    test_config = [
        {
            "type": "MOCK",
            "call": {"name": "test_make_suite_call_1"},
            "line": 1,
        },
    ]
    # write as yaml
    with open(
        temporary_directory.joinpath("calls.yaml"), "w", encoding="UTF-8"
    ) as file:
        file.write(dump(test_config))

    test_config_2 = [
        {
            "type": "MOCK",
            "call": {"name": "test_make_suite_call_2"},
            "line": 1,
        },
    ]
    # write as yaml
    with open(
        temporary_directory.joinpath("calls_2.yaml"), "w", encoding="UTF-8"
    ) as file:
        file.write(dump(test_config_2))

    assert "test_make_suite_call_1" not in called
    call["project"] = temporary_directory.as_posix()
    make_suite_call(call)
    assert called["test_make_suite_call_1"] is True

    assert "test_make_suite_call_2" not in called
    call["calls"] = "calls_2.yaml"
    make_suite_call(call)
    assert called["test_make_suite_call_2"] is True

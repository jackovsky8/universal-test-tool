"""
This module contains tests for the selenium plugin.
"""
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from shutil import rmtree
from typing import Dict

import pytest
import test_tool_suite_plugin.main as test_tool_suite_plugin
import yaml

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

    call = deepcopy(test_tool_suite_plugin.default_suite_call)

    temporary_directory = Path(tempfile.gettempdir()).joinpath(
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
        file.write(yaml.dump(test_data))

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
        file.write(yaml.dump(test_config))

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
        file.write(yaml.dump(test_config_2))

    assert "test_make_suite_call_1" not in called
    call["project"] = temporary_directory.as_posix()
    test_tool_suite_plugin.make_suite_call(call)
    assert called["test_make_suite_call_1"] is True

    assert "test_make_suite_call_2" not in called
    call["calls"] = "calls_2.yaml"
    test_tool_suite_plugin.make_suite_call(call)
    assert called["test_make_suite_call_2"] is True

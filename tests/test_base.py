"""
This module contains tests for the base module.
"""
import sys
import tempfile
from pathlib import Path
from shutil import rmtree
from typing import Any, Dict, List

import pytest
import yaml
from test_tool.base import (Call, CallType, import_plugin, load_config_yaml,
                            make_all_calls, run_tests)


@pytest.fixture(scope="function", autouse=True)
def create_test_mock() -> None:
    """
    Create a mock for the test tool plugin.
    """

    class Mock(object):
        """
        A mock class for test plugin.
        """

        default_mock_call: Dict[str, Any] = {}

        @staticmethod
        def make_mock_call(*args, **kwargs) -> None:
            """
            A mock function for make_timing_call.
            """

        @staticmethod
        def augment_mock_call(*args, **kwargs) -> None:
            """
            A mock function for augment_timing_call.
            """

    sys.modules["test_tool_mock_plugin"] = Mock  # type: ignore


def test_import_plugin_existing_plugin() -> None:
    """
    Test the import_plugin function.
    """
    loaded_call_types: Dict[str, CallType] = {}
    plugin = import_plugin("MOCK", loaded_call_types)

    assert plugin is True
    assert "MOCK" in loaded_call_types


def test_import_plugin_non_existing_plugin() -> None:
    """
    Test the import_plugin function.
    """
    loaded_call_types: Dict[str, CallType] = {}
    plugin = import_plugin("NON_EXISTING_PLUGIN", loaded_call_types)

    assert plugin is False


def test_import_plugin_no_members_required() -> None:
    """
    Test the import_plugin function.
    """

    class EmptyMock(object):
        """
        A empty mock class for test plugin.
        """

    sys.modules["test_tool_mock_plugin"] = EmptyMock  # type: ignore
    loaded_call_types: Dict[str, CallType] = {}

    plugin = import_plugin("MOCK", loaded_call_types)

    assert plugin is True


def test_import_plugin_wrong_members_type() -> None:
    """
    Test the import_plugin function.
    """

    class WrongMock(object):
        """
        A wrong mock class for test plugin.
        """

        default_mock_call: List[str] = []

    sys.modules["test_tool_mock_plugin"] = WrongMock  # type: ignore
    loaded_call_types: Dict[str, CallType] = {}

    with pytest.raises(AttributeError) as excinfo:
        import_plugin("MOCK", loaded_call_types)

    assert (
        "Module test_tool_mock_plugin is not a valid plugin, "
        "default_mock_call is not a <class 'dict'>"
        in str(excinfo.value.args[0])
    )


def test_make_all_calls() -> None:
    """
    Test the make_all_calls function.
    """
    calls: List[Call] = [{"type": "MOCK", "call": {}, "line": 1}]
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, False)

    assert errors == 0


def test_make_all_calls_no_call() -> None:
    """
    Test the make_all_calls function, when no call is provided.
    """
    calls: List[Call] = [{"type": "MOCK", "line": 1}]  # type: ignore
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, False)

    assert errors == 0


def test_make_all_calls_stop_on_error() -> None:
    """
    Test the make_all_calls function, when continue_on_error is False.
    """

    class FailureCallMock(object):
        """
        A mock class for test plugin.
        """

        @staticmethod
        def make_mock_call(
            *args, **kwargs  # pylint: disable=unused-argument
        ) -> None:  # pylint: disable=unused-argument
            """
            A mock function for make_timing_call.
            """
            assert False, "This is a failure"

    sys.modules["test_tool_mock_plugin"] = FailureCallMock  # type: ignore

    calls: List[Call] = [
        {"type": "MOCK", "call": {}, "line": 1},
        {"type": "MOCK", "call": {}, "line": 1},
    ]
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, False)

    assert errors == 1


def test_make_all_calls_not_stop_on_error() -> None:
    """
    Test the make_all_calls function, when continue_on_error is True.
    """

    class FailureCallMock(object):
        """
        A mock class for test plugin.
        """

        @staticmethod
        def make_mock_call(
            *args, **kwargs  # pylint: disable=unused-argument
        ) -> None:  # pylint: disable=unused-argument
            """
            A mock function for make_timing_call.
            """
            assert False, "This is a failure"

    sys.modules["test_tool_mock_plugin"] = FailureCallMock  # type: ignore

    calls: List[Call] = [
        {"type": "MOCK", "call": {}, "line": 1},
        {"type": "MOCK", "call": {}, "line": 1},
    ]
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, True)

    assert errors == 2


def test_make_all_calls_on_default_functions() -> None:
    """
    Test the import_plugin function.
    """

    class EmptyMock(object):
        """
        A empty mock class for test plugin.
        """

    sys.modules["test_tool_mock_plugin"] = EmptyMock  # type: ignore

    calls: List[Call] = [{"type": "MOCK", "line": 1}]  # type: ignore
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, False)

    assert errors == 0


def test_make_all_calls_and_dont_require_all_arguments() -> None:
    """
    Test the import_plugin function.
    """

    class Mock(object):
        """
        A mock class for test plugin.
        """

        @staticmethod
        def make_mock_call(call: Dict[str, Any]) -> None:
            """
            A mock function for make_timing_call.
            """

        @staticmethod
        def augment_mock_call(call: Dict[str, Any]) -> None:
            """
            A mock function for augment_timing_call.
            """

    sys.modules["test_tool_mock_plugin"] = Mock  # type: ignore

    calls: List[Call] = [{"type": "MOCK", "line": 1}]  # type: ignore
    data: Dict[str, Any] = {}
    temporary_directory = Path(tempfile.gettempdir()).joinpath("test_tool")
    temporary_directory.mkdir(exist_ok=True)

    errors = make_all_calls(calls, data, temporary_directory, False)

    assert errors == 0


def test_load_config_yaml() -> None:
    """
    Test the load_config_yaml function.
    """
    path: Path = Path(tempfile.gettempdir()).joinpath(
        "test_tool/config/test.yaml"
    )
    path.parent.mkdir(exist_ok=True, parents=True)

    test_config = {"test_tool": "test_tool_mock_plugin"}
    # write as yaml
    with open(path, "w", encoding="UTF-8") as file:
        file.write(yaml.dump(test_config))

    config = load_config_yaml(path)

    assert config == test_config


def test_load_config_yaml_with_line_numbers() -> None:
    """
    Test the load_config_yaml function.
    """
    path: Path = Path(tempfile.gettempdir()).joinpath(
        "test_tool/config/test.yaml"
    )
    path.parent.mkdir(exist_ok=True, parents=True)

    test_config = "- type: MOCK\n  call:\n    test: 1\n- type: MOCK\n  call:\n    test: 2\n"

    # write as yaml
    with open(path, "w", encoding="utf-8") as file:
        file.write(test_config)

    config = load_config_yaml(path, True)

    assert config == [
        {"type": "MOCK", "call": {"test": 1}, "line": 1},
        {"type": "MOCK", "call": {"test": 2}, "line": 4},
    ]


def test_load_config_yaml_no_file() -> None:
    """
    Test the load_config_yaml function.
    """
    path: Path = Path(tempfile.gettempdir()).joinpath(
        "test_tool/config/test.yaml"
    )
    path.unlink(missing_ok=True)

    with pytest.raises(FileNotFoundError) as excinfo:
        load_config_yaml(path)

    assert excinfo.value.args == (2, "No such file or directory")


def test_run_tests() -> None:
    """
    Test the run_tests function.
    """
    path: Path = Path(tempfile.gettempdir()).joinpath("test_tool/config")
    # remove the folder if it exists
    rmtree(path, ignore_errors=True)
    path.mkdir(exist_ok=True, parents=True)

    test_data = {
        "data": "DATA",
    }
    # write as yaml
    with open(path.joinpath("data.yaml"), "w", encoding="UTF-8") as file:
        file.write(yaml.dump(test_data))
    test_config = [
        {"type": "MOCK", "call": {}, "line": 1},
        {"type": "MOCK", "call": {}, "line": 1},
    ]
    # write as yaml
    with open(path.joinpath("config.yaml"), "w", encoding="UTF-8") as file:
        file.write(yaml.dump(test_config))

    run_tests(path.as_posix(), "config.yaml", "data.yaml", False, "output")

    # Check if the output folder was created
    assert path.joinpath("output").exists()
    assert path.joinpath("output").is_dir()


def test_run_tests_no_data() -> None:
    """
    Test the run_tests function.
    """
    path: Path = Path(tempfile.gettempdir()).joinpath("test_tool/config")
    # remove the folder if it exists
    rmtree(path, ignore_errors=True)
    path.mkdir(exist_ok=True, parents=True)

    test_config = [
        {"type": "MOCK", "call": {}, "line": 1},
        {"type": "MOCK", "call": {}, "line": 1},
    ]
    # write as yaml
    with open(path.joinpath("config.yaml"), "w", encoding="UTF-8") as file:
        file.write(yaml.dump(test_config))

    run_tests(path.as_posix(), "config.yaml", "data.yaml", False, "output")

    # Check if the output folder was created
    assert path.joinpath("output").exists()
    assert path.joinpath("output").is_dir()

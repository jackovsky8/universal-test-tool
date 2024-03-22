"""
This module contains tests for the selenium plugin.
"""
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Dict

import pytest
from test_tool_selenium_plugin.main import (SeleniumAction, SeleniumCall,
                                            augment_selenium_call,
                                            default_selenium_call,
                                            make_selenium_call)
from test_tool_selenium_plugin.native import import_native


def test_import_native() -> None:
    """
    Test the import_native function.
    """
    loaded_call_types: Dict[str, Dict] = {}
    import_native(
        'selenium.webdriver.support.expected_conditions.presence_of_element_located',
        loaded_call_types)

    assert 'selenium' in loaded_call_types
    assert 'webdriver' in loaded_call_types['selenium']
    assert 'support' in loaded_call_types['selenium']['webdriver']
    assert 'expected_conditions' in loaded_call_types['selenium']['webdriver']['support']
    assert 'presence_of_element_located' in loaded_call_types[
        'selenium']['webdriver']['support']['expected_conditions']


def test_import_native_module_not_existing() -> None:
    """
    Test the import_native function with a module that does not exist.
    """
    loaded_call_types: Dict[str, Dict] = {}

    with pytest.raises(ModuleNotFoundError) as e:
        import_native(
            'foo.bar', loaded_call_types)

    assert str(e.value) == "No module named 'foo.bar'"


def test_import_class() -> None:
    """
    Test the import_native function with a class.
    """
    loaded_call_types: Dict[str, Dict] = {}
    import_native(
        'selenium.webdriver.common.by.By', loaded_call_types)

    assert 'selenium' in loaded_call_types
    assert 'webdriver' in loaded_call_types['selenium']
    assert 'common' in loaded_call_types['selenium']['webdriver']
    assert 'by' in loaded_call_types['selenium']['webdriver']['common']
    assert 'By' in loaded_call_types['selenium']['webdriver']['common']['by']


def test_import_native_function_not_existing() -> None:
    """
    Test the import_native function with a function that does not exist.
    """
    loaded_call_types: Dict[str, Dict] = {}

    with pytest.raises(AttributeError) as e:
        import_native(
            'selenium.webdriver.support.expected_conditions.foo', loaded_call_types)

    assert str(
        e.value) == "module 'selenium.webdriver.support.expected_conditions' has no attribute 'foo'"


def test_selenium_plugin_basic() -> None:
    """
    Basic test for the JDBC SQL plugin.
    """
    path: Path = Path(tempfile.gettempdir() + "/page_1.png")
    path.unlink(missing_ok=True)
    call: SeleniumCall = deepcopy(default_selenium_call)
    call['webdriver'] = ['chrome']  # type: ignore
    call['url'] = 'https://www.google.com'
    call['actions'] = [
        # Wait for the search field to load
        {  # type: ignore
            'action': 'selenium.webdriver.support.expected_conditions.presence_of_element_located',
            'args': {
                'type': 'list',
                'value': [
                    {
                        'type': 'list',
                        'value': [
                            {
                                'type': 'native',
                                'value': 'selenium.webdriver.common.by.By.NAME'
                            },
                            'q'
                        ]
                    }
                ]
            }
        },
        # Accept the cookies
        {  # type: ignore
            'action': 'find_element',
            'args': {
                'type': 'list',
                'value': [
                    {
                        'type': 'native',
                        'value': 'selenium.webdriver.common.by.By.XPATH'
                    },
                    '//div[text()="Alle akzeptieren"]/parent::button'
                ],
            },
            'actions': [
                {
                    'action': 'click'
                }
            ]
        },
        # Enter the search term
        {  # type: ignore
            'action': 'find_element',
            'args': {
                'type': 'list',
                'value': [
                    {
                        'type': 'native',
                        'value': 'selenium.webdriver.common.by.By.NAME'
                    },
                    'q'
                ]
            },
            'actions': [
                {
                    'action': 'send_keys',
                    'args': 'wikipedia'
                },
                {
                    'action': 'send_keys',
                    'args': {
                        'type': 'native',
                        'value': 'selenium.webdriver.common.keys.Keys.RETURN'
                    }
                }
            ]
        },
        # Wait for the search results page to load
        {  # type: ignore
            'action': 'sleep',
            'args': 1
        },
        # Save the screenshot
        {  # type: ignore
            'action': 'save_screenshot',
            'args': path.as_posix()
        }
    ]

    augment_selenium_call(call)
    make_selenium_call(call)

    assert path.exists()

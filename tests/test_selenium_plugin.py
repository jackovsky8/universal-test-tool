"""
This module contains tests for the selenium plugin.
"""
from copy import deepcopy
from pathlib import Path
from typing import Dict

import pytest
from test_tool_selenium_plugin.main import (SeleniumAction, SeleniumCall,
                                            augment_selenium_call,
                                            default_selenium_call,
                                            make_selenium_call)


def test_jdbc_sql_plugin_basic() -> None:
    """
    Basic test for the JDBC SQL plugin.
    """
    call: SeleniumCall = deepcopy(default_selenium_call)
    call['base_url'] = "https://www.google.com"
    call['path'] = "/"
    data: Dict = {}

    augment_selenium_call(call, data, Path(__file__))
    make_selenium_call(call, data)

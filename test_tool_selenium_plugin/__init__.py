"""
This module contains the Selenium plugin for the universal test tool.
"""
from .main import (
    augment_selenium_call,
    default_selenium_call,
    make_selenium_call,
)

__all__ = [
    "augment_selenium_call",
    "default_selenium_call",
    "make_selenium_call",
]

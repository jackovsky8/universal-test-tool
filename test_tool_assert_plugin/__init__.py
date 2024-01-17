"""
This module contains the assert plugin for the universal test tool.
"""
from .main import augment_assert_call, default_assert_call, make_assert_call

__all__ = ["augment_assert_call", "default_assert_call", "make_assert_call"]

"""
This module contains the REST plugin for the universal test tool.
"""
from .main import augment_rest_call, default_rest_call, make_rest_call

__all__ = ["augment_rest_call", "default_rest_call", "make_rest_call"]

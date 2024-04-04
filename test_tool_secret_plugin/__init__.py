"""
This module contains the secret plugin for the universal test tool.
"""
from .main import default_secret_call, get_secret, make_secret_call

__all__ = ["default_secret_call", "make_secret_call", "get_secret"]

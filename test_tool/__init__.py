"""
This is the init file for the test_tool package.
"""

from .substitute import recursively_replace_variables
from .utils import DotDict

__all__ = ["recursively_replace_variables"]

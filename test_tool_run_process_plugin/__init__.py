"""
This module contains the run process plugin for the universal test tool.
"""
from .main import (
    augment_run_process_call,
    default_run_process_call,
    make_run_process_call,
)

__all__ = [
    "augment_run_process_call",
    "default_run_process_call",
    "make_run_process_call",
]

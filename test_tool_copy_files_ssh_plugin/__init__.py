"""
This module contains the copy files over SSH plugin for the 
universal test tool.
"""
from .main import (
    augment_copy_files_ssh_call,
    default_copy_files_ssh_call,
    make_copy_files_ssh_call,
)

__all__ = [
    "augment_copy_files_ssh_call",
    "default_copy_files_ssh_call",
    "make_copy_files_ssh_call",
]

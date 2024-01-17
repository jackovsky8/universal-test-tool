"""
This module contains the SSH command plugin for the universal test tool.
"""
from .main import augment_ssh_cmd_call, default_ssh_cmd_call, make_ssh_cmd_call

__all__ = ["augment_ssh_cmd_call", "default_ssh_cmd_call", "make_ssh_cmd_call"]

"""
This module contains the Timing command plugin for the universal test tool.
"""
from .main import augment_timing_call, default_timing_call, make_timing_call

__all__ = ["augment_timing_call", "default_timing_call", "make_timing_call"]

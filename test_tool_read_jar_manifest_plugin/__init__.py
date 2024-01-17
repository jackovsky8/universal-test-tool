"""
This module contains the plugin for reading the manifest of a jar file.
"""
from .main import (
    augment_read_jar_manifest_call,
    default_read_jar_manifest_call,
    make_read_jar_manifest_call,
)

__all__ = [
    "augment_read_jar_manifest_call",
    "default_read_jar_manifest_call",
    "make_read_jar_manifest_call",
]

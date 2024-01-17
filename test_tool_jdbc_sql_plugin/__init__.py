"""
This module contains the JDBC SQL plugin for the universal test tool.
"""
from .main import (
    augment_jdbc_sql_call,
    default_jdbc_sql_call,
    make_jdbc_sql_call,
)

__all__ = [
    "augment_jdbc_sql_call",
    "default_jdbc_sql_call",
    "make_jdbc_sql_call",
]
